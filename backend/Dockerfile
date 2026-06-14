FROM python:3.11-slim

WORKDIR /app

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

COPY requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 180 -r requirements.txt

RUN mkdir -p /app/data /app/uploads /app/files /app/exports

EXPOSE 8016

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8016"]
