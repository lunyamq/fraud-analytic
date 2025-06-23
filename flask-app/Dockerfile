FROM python:3.10

WORKDIR /app
COPY app.py .

RUN pip install flask cassandra-driver

CMD ["python", "app.py"]
