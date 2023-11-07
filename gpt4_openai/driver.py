import json
import os
import platform
import random
import re
import time
import weakref

from selenium.common import exceptions as SeleniumExceptions
from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from singleton import Singleton

cf_challenge_form = (By.ID, 'challenge-form')

chatgpt_textbox = (By.TAG_NAME, 'textarea')
chatgpt_streaming = (By.CLASS_NAME, 'result-streaming')
chatgpt_big_response = (
    By.XPATH, '//div[@class="flex-1 overflow-hidden"]//div[p]')
chatgpt_small_response = (
    By.XPATH,
    '//div[starts-with(@class, "markdown prose w-full break-words")]',
)
chatgpt_alert = (By.XPATH, '//div[@role="alert"]')
chatgpt_dialog = (By.XPATH, '//div[@role="dialog"]')
chatgpt_intro = (By.ID, 'headlessui-portal-root')
chatgpt_login_btn = (By.XPATH, '//button[text()="Log in"]')
chatgpt_login_h1 = (By.XPATH, '//h1[text()="Welcome back"]')
chatgpt_logged_h1 = (By.XPATH, '//h1[text()="ChatGPT"]')

chatgpt_new_chat = (By.LINK_TEXT, 'New chat')
chatgpt_clear_convo = (By.LINK_TEXT, 'Clear conversations')
chatgpt_confirm_clear_convo = (By.LINK_TEXT, 'Confirm clear conversations')
chatgpt_chats_list_first_node = (
    By.XPATH,
    "//li[@class='relative z-[15]']//a",
)

stop_generating = (By.XPATH, "//button[contains(., 'Stop generating')]")
regenerate_response = (By.XPATH, "//*[.//div[contains(text(), 'Regenerate')]]")


class ChatGptDriver(metaclass=Singleton):
    """
    An unofficial Python wrapper for OpenAI's ChatGPT API
    """

    def __init__(
            self,
            session_token,
            conversation_id: str = '',
            login_cookies_path: str = '',
            model: str = 'gpt4'
    ):
        """
        Initialize the ChatGPT object\n
        :param session_token: The session token to use for
            authentication
        :param conversation_id: The conversation ID to use for the
            chat session
        :param login_cookies_path: The path to the cookies file to use
            for authentication
        :param moderation: Whether to enable message moderation
        """

        self.__session_token = session_token
        self.conversation_id = conversation_id

        self._model = model
        self._chatgpt_chat_url = 'https://chat.openai.com'

        self.conversation_id_pattern = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        )
        self.is_active = False

        if not self.__session_token:
            raise ValueError(
                'Please provide a session token'
            )

        self.__init_browser()
        weakref.finalize(self, self.__del__)

    def _get_url(self):
        if self.conversation_id:
            return (f'{self._chatgpt_chat_url}/c/{self.conversation_id}/'
                    f'?model={self._model}')
        return f"{self._chatgpt_chat_url}/?model={self._model}"

    def close_driver(self):
        """Close the browser and display"""
        self.is_active = False
        if hasattr(self, 'driver'):
            self.driver.quit()
        if hasattr(self, 'display'):
            self.display.stop()

    def __enter__(self):
        self.__init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()

    def __del__(self):
        """
        Close the browser and display
        """
        self.close_driver()

    def __init_browser(self) -> None:
        """
        Initialize the browser
        """
        self.is_active = True
        if platform.system() == 'Linux' and 'DISPLAY' not in os.environ:
            try:
                from pyvirtualdisplay import Display

                self.display = Display()
            except ModuleNotFoundError:
                raise ValueError(
                    'Please install PyVirtualDisplay to start a virtual '
                    'display by running `pip install PyVirtualDisplay`'
                )
            except FileNotFoundError as e:
                if 'No such file or directory: \'Xvfb\'' in str(e):
                    raise ValueError(
                        'Please install Xvfb to start a virtual display by '
                        'running `sudo apt install xvfb`'
                    )
                raise e
            self.display.start()

        driver_path = ChromeDriverManager(
            chrome_type=ChromeType.CHROMIUM).install()
        options = ChromeOptions()
        if os.getenv('CHROMIUM_PATH'):
            options.binary_location = os.environ['CHROMIUM_PATH']
        service = ChromeService(executable_path=driver_path)
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)

        self.driver.execute_cdp_cmd(
            'Network.setCookie',
            {
                'domain': 'chat.openai.com',
                'path': '/',
                'name': '__Secure-next-auth.session-token',
                'value': self.__session_token,
                'httpOnly': True,
                'secure': True,
            },
        )

        self.__ensure_cf()

    def __ensure_cf(self, retry: int = 3) -> None:
        """
        Ensure Cloudflare cookies are set\n
        :param retry: Number of retries
        """
        original_window = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')

        self.driver.get('https://chat.openai.com/api/auth/session')
        try:
            WebDriverWait(self.driver, 3).until_not(
                ec.presence_of_element_located(cf_challenge_form)
            )
        except SeleniumExceptions.TimeoutException:
            if retry > 0:
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return self.__ensure_cf(retry - 1)
            self.close_driver()
            raise ValueError('Cloudflare challenge failed')

        response = self.driver.page_source
        if response[0] != '{':
            response = self.driver.find_element(By.TAG_NAME, 'pre').text
        response = json.loads(response)
        if (not response) or (
                'error' in response and response['error'] ==
                'RefreshAccessTokenError'
        ):
            self.close_driver()
            raise ValueError('Invalid session token')

        self.driver.close()
        self.driver.switch_to.window(original_window)

    def __check_blocking_elements(self) -> None:
        """
        Check for blocking elements and dismiss them
        """

        try:
            # FInd a button to dismiss the dialog with
            # class="btn relative btn-primary" inside the div[@role="dialog"]
            btn_to_dismiss = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog"]//button[@class="btn relative '
                     'btn-primary"]'))
            )
            if btn_to_dismiss:
                self.driver.execute_script('arguments[0].click()',
                                           btn_to_dismiss)
        except Exception:
            pass

        try:
            # for 3 times
            i = 0
            while i <= 2:
                self.__sleep(0.4)
                if i != 2:
                    # get the button with
                    # class="btn relative btn-neutral ml-auto"
                    btn = WebDriverWait(self.driver, 5).until(
                        ec.presence_of_element_located(
                            (By.XPATH,
                             '//button[@class="btn relative btn-neutral '
                             'ml-auto"]'))
                    )
                else:
                    # get the button with class="btn relative
                    # btn-primary ml-auto"
                    btn = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located(
                            (By.XPATH, '//button[@class="btn relative '
                                       'btn-primary ml-auto"]'))
                    )
                if btn:
                    self.driver.execute_script('arguments[0].click()', btn)
                i += 1
        except Exception:
            pass

    def __stream_message(self):
        try:
            prev_content = ''
            while True:
                result_streaming = self.driver.find_elements(*chatgpt_streaming)
                responses = self.driver.find_elements(*chatgpt_big_response)
                if responses:
                    response = responses[-1]
                    if 'text-red' in response.get_attribute('class'):
                        raise ValueError(response.text)
                if result_streaming:
                    content = result_streaming[-1].text
                else:
                    content = ''
                if content != prev_content:
                    yield content[len(prev_content):]
                    prev_content = content
                if not result_streaming:
                    break
                self.__sleep(0.1)
        finally:
            self.close_driver()

    def send_message(self, message: str, model='gpt-4-browsing'):
        if not self.is_active:
            self.__init_browser()
        self._model = model
        self.driver.get(self._get_url())
        self.__check_blocking_elements()

        cur_hwnd = self.driver.current_window_handle
        for hwnd in self.driver.window_handles:
            if hwnd != cur_hwnd:
                self.driver.switch_to.window(hwnd)
                self.driver.close()
        # Wait for page to load
        try:
            WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable(chatgpt_textbox)
            )
        except SeleniumExceptions.ElementClickInterceptedException:
            pass

        # Check for dismiss button
        try:
            WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Dismiss')]"))
            ).click()
            self.__sleep()
        except Exception:
            pass

        try:
            textbox = WebDriverWait(self.driver, 3).until(
                ec.element_to_be_clickable(chatgpt_textbox)
            )
            textbox.click()
        except SeleniumExceptions.ElementClickInterceptedException:
            self.__check_blocking_elements()
            textbox = WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable(chatgpt_textbox)
            )
            textbox.click()

        self.driver.execute_script(
            '''
        var element = arguments[0], txt = arguments[1];
        element.value += txt;
        element.dispatchEvent(new Event("change"));
        ''',
            textbox,
            message,
        )

        self.__sleep(0.5)
        textbox.send_keys(Keys.ENTER)
        button = textbox.find_element(By.XPATH, "./ancestor::div/button")
        button.click()
        return self.__stream_message()

    @staticmethod
    def __sleep(sec=1.0, multiplier=2) -> None:
        """
        Random sleep to avoid detection
        """
        time.sleep(random.uniform(sec, sec * multiplier))
