FROM apache/spark:3.5.7-scala2.12-java17-python3-ubuntu

USER root

# Install Python dependencies and netcat
RUN apt-get update && apt-get install -y \
    python3-pip \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install required Python packages
RUN pip3 install --no-cache-dir \
    pyspark==3.5.0 \
    kafka-python==2.0.2 \
    pymongo==4.6.0 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    psycopg2-binary==2.9.9 \
    redis==5.0.1

# Set working directory
WORKDIR /opt/spark-apps

# Copy Spark applications
COPY spark_streaming.py .
COPY batch_processing.py .
COPY entrypoint.sh .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Create Ivy cache directory and set permissions
RUN mkdir -p /opt/spark/.ivy2/cache && \
    mkdir -p /opt/spark/.ivy2/jars && \
    chown -R spark:spark /opt/spark/.ivy2

# Switch back to spark user
USER spark

# Set environment variables for Ivy cache
ENV IVY_HOME=/opt/spark/.ivy2

ENTRYPOINT ["/opt/spark-apps/entrypoint.sh"]
