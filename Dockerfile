FROM python:3.12

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

COPY main.py /app/main.py

CMD ["python", "/app/main.py"]