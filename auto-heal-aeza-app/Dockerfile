FROM python:3.11.2-alpine3.17

WORKDIR /app

COPY ./ /app

ENV PATH="/home/app/.local/bin:${PATH}"

RUN adduser -D app && \
    chown -R app:app /app

USER app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]