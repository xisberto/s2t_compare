FROM python:3.11-alpine

WORKDIR /app/

RUN apk add --no-cache g++

COPY ./requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ /app/

ENTRYPOINT ["python", "main.py", "-b"]