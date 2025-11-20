FROM tensorflow/tensorflow:2.13.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies for full ML stack (Prophet, LightGBM, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gfortran \
      libgomp1 \
      git \
      make \
      unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install full requirements for R&D (heavy)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY . /app

# Default to periodic run (can override LOOP_SECONDS via env)
CMD ["python", "-u", "run_pipeline.py"]
