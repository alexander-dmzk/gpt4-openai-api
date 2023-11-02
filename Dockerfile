FROM python:3.11

ADD . /app
WORKDIR /app
RUN apt-get update && \
    apt-get install -y chromium xvfb && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-m", "server.instance"]
