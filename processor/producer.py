# producer.py
from kafka import KafkaProducer
from tqdm import tqdm
import pandas as pd
import time
import os

KAFKA_TOPIC = "fraud-topic"
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "kafka:9092")


df_test = pd.read_csv('creditcard.csv')

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: str(v).encode("utf-8")
)

for _, row in tqdm(df_test.iterrows(), total=len(df_test)):
    transaction = row.to_json()
    producer.send(KAFKA_TOPIC, value=transaction)
    time.sleep(0.001)
    
producer.flush()
producer.close()
