FROM python:3.12-slim

WORKDIR /home/node/files/scriptssm

COPY . .

RUN pip install --no-cache-dir -r requirements.txt || true
