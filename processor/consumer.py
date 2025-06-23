# consumer.py 
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.functions import vector_to_array
from pyspark.sql.types import *
from pyspark.ml import PipelineModel
import os

spark = SparkSession.builder \
    .appName("FraudDetectionStreaming") \
    .config("spark.cassandra.connection.host", "cassandra") \
    .getOrCreate()

spark.sparkContext.setLogLevel("OFF")

model = PipelineModel.load("fraud_model")

schema = StructType([
    StructField("Time", DoubleType()),
    StructField("V1", DoubleType()),
    StructField("V2", DoubleType()),
    StructField("V3", DoubleType()),
    StructField("V4", DoubleType()),
    StructField("V5", DoubleType()),
    StructField("V6", DoubleType()),
    StructField("V7", DoubleType()),
    StructField("V8", DoubleType()),
    StructField("V9", DoubleType()),
    StructField("V10", DoubleType()),
    StructField("V11", DoubleType()),
    StructField("V12", DoubleType()),
    StructField("V13", DoubleType()),
    StructField("V14", DoubleType()),
    StructField("V15", DoubleType()),
    StructField("V16", DoubleType()),
    StructField("V17", DoubleType()),
    StructField("V18", DoubleType()),
    StructField("V19", DoubleType()),
    StructField("V20", DoubleType()),
    StructField("V21", DoubleType()),
    StructField("V22", DoubleType()),
    StructField("V23", DoubleType()),
    StructField("V24", DoubleType()),
    StructField("V25", DoubleType()),
    StructField("V26", DoubleType()),
    StructField("V27", DoubleType()),
    StructField("V28", DoubleType()),
    StructField("Amount", DoubleType()),
    StructField("Class", DoubleType())
])

KAFKA_TOPIC = "fraud-topic"
KAFKA_BOOTSTRAP  = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

stream_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

parsed_df = stream_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")


predictions = model.transform(parsed_df)
fraud_transactions = predictions \
    .filter((col("prediction") == 1.0) | (col("Class") == 1.0)) \
    .withColumn("probability_array", vector_to_array("probability")) \
    .withColumn("fraud_probability", col("probability_array")[1]) \
    .withColumnRenamed("Time", "time") \
    .withColumnRenamed("Amount", "amount") \
    .withColumnRenamed("Class", "clazz") \
    .select("time", "amount", "fraud_probability", "prediction", "clazz")

def process_batch(batch_df, batch_id):
    if batch_df.head(1):
        batch_df = batch_df \
            
        
        batch_df.show(truncate=False)
    
    batch_df.write \
             .format("org.apache.spark.sql.cassandra") \
             .mode("append") \
             .options(table="alerts", keyspace="fraud") \
             .save()

query = fraud_transactions.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .start()

query.awaitTermination()
