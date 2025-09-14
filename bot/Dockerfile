FROM python:3.12.3

WORKDIR /bot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY data.json .
COPY brevityTerms.csv .

CMD ["python", "main.py"]