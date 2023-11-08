import subprocess
import time
from argparse import ArgumentParser

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument("--host", "-H", type=str,
                           default='0.0.0.0',
                           help="scrapers api server host")
    argparser.add_argument("--port", "-P", type=str,
                           default='3000',
                           help="scrapers api server port")
    args = argparser.parse_args()
    while True:
        subprocess.call([
            'python',
            '-m',
            'server.instance',
            '--host',
            args.host,
            '--port',
            args.port
        ])
        print('Server exited. Sleep and try to rerun')
        time.sleep(5)
