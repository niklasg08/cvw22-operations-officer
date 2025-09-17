FROM python:3.12.3

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /src/bot

COPY src/bot/main.py .

CMD ["python", "main.py"]