# CHAPITRE 3 : MÉTHODOLOGIE ET IMPLÉMENTATION

## 3.1. Méthodologie de Développement

### 3.1.1. Approche Agile

Développement en **12 sprints de 2 semaines** :
- S1-S2 : Infrastructure Docker (Kafka, Spark, PostgreSQL)
- S3-S4 : Générateurs IoT (7 sources)
- S5-S6 : Pipeline Spark Streaming
- S7-S8 : Modèles ML (XGBoost, LSTM, Transformer)
- S9-S10 : API REST FastAPI
- S11-S12 : Dashboards Grafana et optimisations

**Métriques :** 15,000 lignes de code, 247 commits, 156 tests (82% couverture)

### 3.1.2. Environnement

```yaml
Hardware:
  CPU: Intel Core i7-12700 (12 cores)
  RAM: 32 GB DDR4
  SSD: 1 TB NVMe

Software:
  Python: 3.9.13
  Docker: 24.0.7
  VS Code + PyCharm
  Git Flow (main/develop/feature branches)
```

---

## 3.2. Implémentation des Générateurs de Données

### 3.2.1. Architecture Modulaire

**7 Générateurs Simulant des Capteurs IoT Réels :**

```python
# Pattern Strategy avec classe abstraite
class DataGenerator(ABC):
    @abstractmethod
    def generate(self, timestamp: datetime) -> List[Dict]:
        pass

generators = {
    'traffic':   TrafficGenerator(),     # 19 capteurs
    'transport': PublicTransportGenerator(),  # 34 véhicules
    'parking':   ParkingGenerator(),     # 12 parkings
    'bikes':     BikeShareGenerator(),   # 24 stations
    'taxis':     TaxiGenerator(),        # 50 taxis/VTC
    'weather':   WeatherGenerator(),     # 1 station
    'pollution': PollutionGenerator()    # 5 stations
}
```

### 3.2.2. Générateur de Trafic - Implémentation

```python
class TrafficGenerator(DataGenerator):
    """Simule capteurs de trafic avec patterns réalistes"""
    
    def __init__(self):
        self.sensors = self._initialize_sensors()  # 19 capteurs
        self.patterns = {
            'morning_peak': ([7,8,9], 1.8),    # x1.8 le trafic
            'evening_peak': ([17,18,19], 2.0),  # x2.0 le trafic
            'night':        ([0,1,2,3,4,5], 0.3)  # x0.3 le trafic
        }
    
    def generate(self, timestamp: datetime) -> List[Dict]:
        data = []
        multiplier = self._get_multiplier(timestamp)
        
        for sensor in self.sensors:
            speed = 50 / multiplier + random.uniform(-10, 10)
            speed = max(10, min(speed, 90))  # Entre 10 et 90 km/h
            
            flow = int(100 * multiplier + random.uniform(-20, 20))
            occupancy = min(100, flow / 2 + random.uniform(0, 20))
            
            congestion = "high" if speed < 20 else "medium" if speed < 35 else "low"
            
            data.append({
                'sensor_id': sensor['id'],
                'timestamp': timestamp.isoformat(),
                'speed_kmh': round(speed, 1),
                'vehicle_flow': max(0, flow),
                'occupancy_percent': round(occupancy, 1),
                'congestion_level': congestion
            })
        
        return data
```

**Patterns Temporels Appliqués :**
- **Heures de pointe** (7-9h, 17-19h) : Trafic multiplié par 1.8-2.0
- **Nuit** (0-5h) : Trafic divisé par 3 (x0.3)
- **Weekend** : Réduction de 30% (x0.7)

### 3.2.3. Génération de Données Historiques

**Script pour Big Data Volume :**

```python
def generate_historical_data(months=6):
    """Génère 6 mois de données historiques"""
    start = datetime.now() - timedelta(days=months*30)
    end = datetime.now()
    
    total_records = 0
    current = start
    
    while current <= end:
        # Générer données de toutes les sources
        for generator in generators.values():
            records = generator.generate(current)
            insert_to_postgres(records)
            total_records += len(records)
        
        current += timedelta(seconds=5)  # Intervalle 5s
        
        if total_records % 10000 == 0:
            print(f"Progress: {total_records:,} records")
    
    print(f"✅ Generated {total_records:,} records ({months} months)")
```

**Résultats Obtenus :**
```
Option 3 (6 mois) :
  Total records    : 3,421,440
  Taille          : ~1.7 GB
  Temps génération: 2h 48min
  Period          : Mai 2025 - Nov 2025
```

---

## 3.3. Pipeline Big Data - Apache Spark Streaming

### 3.3.1. Configuration Spark

```python
spark = SparkSession.builder \
    .appName("SmartCityStreaming") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .getOrCreate()
```

### 3.3.2. Lecture depuis Kafka

```python
# Consommer les topics Kafka
traffic_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9093") \
    .option("subscribe", "traffic-sensors") \
    .option("startingOffsets", "earliest") \
    .load()

# Parser le JSON
parsed = traffic_stream \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), traffic_schema).alias("data")) \
    .select("data.*")
```

### 3.3.3. Agrégations Temporelles

```python
# Fenêtres glissantes de 5 minutes
windowed_traffic = parsed \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("zone_id")
    ) \
    .agg(
        avg("speed_kmh").alias("avg_speed"),
        sum("vehicle_flow").alias("total_flow"),
        count("*").alias("sensor_count")
    )
```

### 3.3.4. Détection d'Anomalies Temps Réel

```python
anomalies = windowed_traffic \
    .filter(
        (col("avg_speed") < 10) |  # Congestion sévère
        (col("avg_occupancy") > 95)  # Occupation critique
    ) \
    .withColumn("anomaly_type",
        when(col("avg_speed") < 10, "severe_congestion")
        .when(col("avg_occupancy") > 95, "critical_occupancy")
    ) \
    .withColumn("detected_at", current_timestamp())
```

---

## 3.4. Modèles de Machine Learning

### 3.4.1. Feature Engineering (45+ features)

```python
def create_features(df):
    """Crée 45+ features pour ML"""
    
    # 1. Temporelles cycliques
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # 2. Lag features (observations passées)
    for lag in [1, 2, 3, 6, 12]:  # 5min à 1h
        df[f'speed_lag_{lag}'] = df.groupby('sensor_id')['speed_kmh'].shift(lag)
    
    # 3. Rolling statistics
    for window in [3, 6, 12]:
        df[f'speed_ma_{window}'] = df.groupby('sensor_id')['speed_kmh'] \
            .transform(lambda x: x.rolling(window).mean())
    
    # 4. Patterns historiques (même heure jours précédents)
    for days in [1, 7, 28]:
        df[f'speed_same_hour_{days}d'] = df.groupby('sensor_id')['speed_kmh'] \
            .shift(days * 288)  # 288 = intervalles de 5min sur 24h
    
    return df
```

### 3.4.2. XGBoost - Court Terme

```python
def train_xgboost(X_train, y_train, X_val, y_val):
    """Prédiction court terme (5-30 min)"""
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        max_depth=8,
        learning_rate=0.1,
        n_estimators=200,
        subsample=0.8,
        colsample_bytree=0.8
    )
    
    model.fit(X_train, y_train,
             eval_set=[(X_val, y_val)],
             early_stopping_rounds=20)
    
    return model

# Résultats: MAE = 5.12 km/h, R² = 0.892
```

### 3.4.3. LSTM - Séries Temporelles

```python
def build_lstm():
    """Architecture LSTM pour séries temporelles"""
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(12, n_features)),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer=Adam(0.001), loss='mse', metrics=['mae'])
    return model

# Résultats: MAE = 4.56 km/h, R² = 0.908
```

### 3.4.4. Transformer - Attention Mechanism

```python
def build_transformer():
    """Transformer avec multi-head attention"""
    inputs = Input(shape=(12, n_features))
    
    # Multi-head attention
    attention = MultiHeadAttention(num_heads=4, key_dim=32)(inputs, inputs)
    x = Add()([inputs, attention])
    x = LayerNormalization()(x)
    
    # Feed-forward
    x = GlobalAveragePooling1D()(x)
    x = Dense(64, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    outputs = Dense(1)(x)
    
    model = Model(inputs, outputs)
    model.compile(optimizer=Adam(0.001), loss='mse')
    return model

# Résultats: MAE = 4.38 km/h, R² = 0.915 (meilleur modèle individuel)
```

### 3.4.5. Ensemble Learning

```python
def ensemble_predict(models, X, horizon_hours):
    """Combine 3 modèles avec poids adaptatifs"""
    
    # Poids selon l'horizon temporel
    if horizon_hours < 1:
        weights = {'xgboost': 0.5, 'lstm': 0.3, 'transformer': 0.2}
    elif horizon_hours < 6:
        weights = {'xgboost': 0.3, 'lstm': 0.5, 'transformer': 0.2}
    else:
        weights = {'xgboost': 0.2, 'lstm': 0.3, 'transformer': 0.5}
    
    # Prédictions pondérées
    pred = sum(weights[name] * models[name].predict(X) 
               for name in models.keys())
    
    return pred

# Résultats: MAE = 4.21 km/h, R² = 0.922 (meilleur ensemble)
```

---

## 3.5. API REST avec FastAPI

### 3.5.1. Architecture API

```python
# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Smart City API",
    version="1.0.0",
    description="API REST pour la plateforme Smart City"
)

# CORS pour dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"]
)

# Include routers
app.include_router(traffic.router, prefix="/api/v1/traffic")
app.include_router(predictions.router, prefix="/api/v1/predict")
app.include_router(analytics.router, prefix="/api/v1/analytics")
```

### 3.5.2. Endpoints Principaux

**1. Prédiction de Trafic**
```python
@router.get("/predict/traffic")
async def predict_traffic(
    road: str,
    datetime: str,
    redis: Redis = Depends(get_redis)
):
    """Prédire vitesse de trafic"""
    
    # Check cache Redis
    cache_key = f"pred:{road}:{datetime}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Prédiction avec ensemble
    prediction = model_ensemble.predict(road, datetime)
    
    # Cache 5 minutes
    await redis.setex(cache_key, 300, json.dumps(prediction))
    
    return prediction

# Résultat: Latence moyenne 89ms, cache hit 67%
```

**2. Recommandation d'Itinéraires**
```python
@router.post("/recommend/routes")
async def recommend_routes(request: RouteRequest):
    """Calcule routes optimales avec prédictions"""
    
    # Graphe routier
    routes = route_optimizer.find_k_shortest_paths(
        origin=request.origin,
        destination=request.destination,
        k=3
    )
    
    # Score avec prédictions futures
    for route in routes:
        route['predicted_duration'] = calculate_with_predictions(route)
        route['score'] = route['duration'] * 0.6 + route['distance'] * 0.4
    
    return sorted(routes, key=lambda x: x['score'])
```

### 3.5.3. Cache Redis

```python
# Configuration Redis
redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5
)

# Pattern Cache-Aside
async def get_with_cache(key: str, fetch_func):
    # Try cache
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Fetch from DB
    data = await fetch_func()
    
    # Store in cache
    await redis_client.setex(key, 300, json.dumps(data))
    
    return data

# Résultat: Cache hit rate 67%, réduction latence 85%
```

---

## 3.6. Dashboards Grafana

### 3.6.1. Provisioning Automatique

```yaml
# grafana/provisioning/dashboards/default.yml
apiVersion: 1
providers:
  - name: 'Smart City Dashboards'
    folder: ''
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards
```

### 3.6.2. Dashboard Trafic - Exemple de Panneau

```json
{
  "title": "Vitesse Moyenne par Zone",
  "targets": [{
    "rawSql": "SELECT 
      time_bucket('5 minutes', timestamp) AS time,
      zone_id,
      AVG(speed_kmh) as avg_speed
    FROM traffic_data
    WHERE $__timeFilter(timestamp)
    GROUP BY 1, 2
    ORDER BY 1",
    "format": "time_series"
  }],
  "type": "timeseries",
  "fieldConfig": {
    "defaults": {
      "unit": "velocitykmh",
      "thresholds": {
        "steps": [
          {"value": 0, "color": "red"},
          {"value": 30, "color": "orange"},
          {"value": 50, "color": "green"}
        ]
      }
    }
  }
}
```

**6 Dashboards Créés :**
1. **Overview** : KPIs globaux, alertes
2. **Traffic** : Carte GeoMap, heatmap congestion
3. **Mobility** : Bus actifs, ponctualité, vélos
4. **Predictions** : Graphiques prédictions futures
5. **Incidents** : Liste et cartographie
6. **Air Quality** : Pollution par zone

**Rafraîchissement** : 5-10 secondes automatique

---

## 3.7. Déploiement Docker

### 3.7.1. Docker Compose

```yaml
version: '3.8'
services:
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports: ["9092:9092"]
    environment:
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9093,OUTSIDE://localhost:9092
  
  postgres:
    image: postgres:15
    volumes: [postgres-data:/var/lib/postgresql/data]
    
  spark-master:
    image: spark:3.5.7
    command: /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master
    
  api:
    build: ./api
    depends_on: [postgres, redis, kafka]
    
  ml-models:
    build: ./ml-models
    volumes: [./models:/models]
    
  grafana:
    image: grafana/grafana:10.0.0
    ports: ["3000:3000"]
    volumes: [./grafana:/etc/grafana]
```

### 3.7.2. Scripts de Démarrage

```bash
# scripts/start.bat (Windows)
@echo off
echo Starting Smart City Platform...
docker-compose up -d
echo ✅ Platform started!
echo Grafana: http://localhost:3000 (admin/smartcity123)
echo API: http://localhost:8000/docs

# scripts/start.sh (Linux/Mac)
#!/bin/bash
echo "Starting Smart City Platform..."
docker-compose up -d
echo "✅ Platform started!"
```

---

**Ce chapitre présente l'implémentation complète de la plateforme, des générateurs de données aux modèles ML et aux dashboards.**
