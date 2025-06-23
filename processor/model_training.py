# model_training.py
from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.classification import RandomForestClassifier


spark = SparkSession.builder.master("local[*]").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = (
    spark.read.format("csv")
         .option("header", "true")
         .option("inferSchema", "true")
         .load("creditcard.csv")
)

feature_columns = [c for c in df.columns if c.startswith("V")]
vectorizer = VectorAssembler(
    inputCols=feature_columns,
    outputCol="features",
    handleInvalid="skip"
)

rf = RandomForestClassifier(labelCol="Class",
                            featuresCol="features",
                            maxDepth=5)

df_train, df_test = df.randomSplit([0.7, 0.3], seed=1)

pipeline = Pipeline(stages=[vectorizer, rf])
model = pipeline.fit(df_train)
model.write().overwrite().save("fraud_model")
print("Model saved!")

predictions = model.transform(df_test)
evaluator = BinaryClassificationEvaluator(labelCol="Class", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
auc = evaluator.evaluate(predictions)
print(f"[MODEL EVALUATION] AUC = {auc:.4f}")
