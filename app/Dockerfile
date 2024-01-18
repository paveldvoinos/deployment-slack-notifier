FROM python:3.10-alpine

RUN apk --no-cache add bash curl vim jq
RUN pip install pipenv

WORKDIR /app

COPY app/ /app

RUN pipenv install --dev --system --deploy

ENV PYTHONUNBUFFERED=1
ENV PYTHONBUFFERED=0

EXPOSE 8080

CMD ["python", "app.py"]