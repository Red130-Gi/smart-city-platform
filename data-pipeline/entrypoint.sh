#!/bin/bash
set -e

echo "================================================"
echo "Starting Spark Streaming Jobs for Smart City"
echo "================================================"

# Wait for dependencies to be ready
echo "Waiting for Kafka to be ready..."
until nc -z kafka 9093; do
  echo "Kafka not ready yet. Waiting..."
  sleep 5
done
echo "✓ Kafka is ready"

echo "Waiting for PostgreSQL to be ready..."
until nc -z postgres 5432; do
  echo "PostgreSQL not ready yet. Waiting..."
  sleep 5
done
echo "✓ PostgreSQL is ready"

echo "Waiting for MongoDB to be ready..."
until nc -z mongodb 27017; do
  echo "MongoDB not ready yet. Waiting..."
  sleep 5
done
echo "✓ MongoDB is ready"

# Wait a bit more for services to stabilize
echo "Waiting for services to stabilize..."
sleep 15

# Check which job to run (default: streaming)
JOB_TYPE=${SPARK_JOB_TYPE:-streaming}

echo "================================================"
echo "Starting Spark Job: $JOB_TYPE"
echo "================================================"

if [ "$JOB_TYPE" = "streaming" ]; then
    echo "Launching Spark Streaming job..."
    exec /opt/spark/bin/spark-submit \
        --master local[*] \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.2.0 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.driver.memory=2g \
        --conf spark.executor.memory=2g \
        --conf spark.jars.ivy=/opt/spark/.ivy2 \
        /opt/spark-apps/spark_streaming.py
elif [ "$JOB_TYPE" = "batch" ]; then
    echo "Launching Spark Batch Processing job..."
    exec /opt/spark/bin/spark-submit \
        --master local[*] \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.2.0 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.driver.memory=2g \
        --conf spark.executor.memory=2g \
        --conf spark.jars.ivy=/opt/spark/.ivy2 \
        /opt/spark-apps/batch_processing.py
else
    echo "Unknown job type: $JOB_TYPE"
    echo "Valid options: streaming, batch"
    exit 1
fi
