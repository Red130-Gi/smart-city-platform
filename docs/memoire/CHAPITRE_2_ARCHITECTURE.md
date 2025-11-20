# CHAPITRE 2 : ANALYSE ET CONCEPTION

## 2.1. Analyse des Besoins

### 2.1.1. Besoins Fonctionnels

**BF1. Collecte de Données Multi-Sources**
- Intégrer 7+ sources de données urbaines (trafic, transport, parking, vélos, taxis, météo, pollution)
- Supporter différents formats (JSON, CSV, XML)
- Gérer des fréquences de collecte variées (1s à 5min)
- Garantir la traçabilité de l'origine des données

**BF2. Traitement Temps Réel**
- Ingestion de flux de données en streaming continu
- Traitement en micro-batches (< 30 secondes)
- Agrégations temporelles (fenêtres de 5 minutes)
- Détection d'anomalies en temps réel

**BF3. Prédiction de Trafic**
- Prédire la vitesse de circulation 5min à 12h à l'avance
- Fournir des intervalles de confiance (95%)
- Prédictions par capteur et par zone géographique
- Mise à jour des modèles toutes les 24h

**BF4. Recommandation d'Itinéraires**
- Calculer routes optimales origine-destination
- Proposer 3+ alternatives avec métriques (temps, distance, congestion)
- Intégrer les prédictions de trafic futures
- Optimisation multi-objectifs (temps, émissions, coût)

**BF5. Détection d'Anomalies et Incidents**
- Identifier congestions anormales en temps réel
- Détecter incidents automatiquement (seuils adaptatifs)
- Classifier par type (accident, panne, travaux, événement)
- Alerter les opérateurs en < 2 minutes

**BF6. Visualisation et Dashboards**
- 6+ dashboards temps réel rafraîchis toutes les 5-10s
- Cartes géographiques interactives
- Graphiques de tendances historiques
- Alertes visuelles sur seuils critiques

**BF7. API REST**
- 20+ endpoints pour accès aux données et prédictions
- Authentification et limitation de débit (rate limiting)
- Documentation Swagger auto-générée
- Versioning des APIs (v1, v2)

**BF8. Administration et Monitoring**
- Monitoring des performances système
- Logs centralisés et structurés
- Métriques de qualité des données
- Interface d'administration

### 2.1.2. Besoins Non Fonctionnels

**BNF1. Performance**
```
Latence API          : < 200ms (P95)
Débit traitement     : > 10,000 records/heure
Latence prédiction ML: < 500ms
Temps réponse cache  : < 10ms
```

**BNF2. Scalabilité**
```
Scalabilité horizontale : Ajout de nœuds sans interruption
Volume de données      : Support de 10x croissance (30M+ records)
Utilisateurs concurrent: > 1,000 utilisateurs simultanés
Partitionnement        : Automatique (Kafka, PostgreSQL)
```

**BNF3. Disponibilité**
```
SLA                 : 99.9% (< 9h downtime/an)
MTBF                : > 720 heures
MTTR                : < 30 minutes
Recovery Time       : < 5 minutes
```

**BNF4. Sécurité**
```
Chiffrement au repos : AES-256
Chiffrement transit  : TLS 1.3
Authentification     : JWT tokens
Autorisation         : RBAC (Role-Based Access Control)
Audit trail          : Logs immutables
```

**BNF5. Qualité des Données**
```
Exactitude      : > 95%
Complétude      : > 98%
Cohérence       : > 96%
Actualité       : < 1 minute de délai
```

**BNF6. Maintenabilité**
```
Couverture tests    : > 80%
Documentation code  : Docstrings obligatoires
Standards coding    : PEP8, Clean Code
Modularité          : Architecture microservices
```

### 2.1.3. Contraintes Techniques et Réglementaires

**Contraintes Techniques**
- **Infrastructure** : Docker 20+, minimum 16GB RAM, 4+ cores CPU
- **Réseau** : Latence inter-services < 10ms (même datacenter)
- **Stockage** : 500GB minimum pour 6 mois de données
- **Langages** : Python 3.9+, SQL
- **Open Source** : Privilégier solutions open-source

**Contraintes Réglementaires**
- **RGPD** : Conformité totale (collecte, traitement, stockage, suppression)
- **Droit à l'oubli** : Suppression complète en < 30 jours
- **Portabilité** : Export données en JSON/CSV
- **Transparence** : Documentation des algorithmes
- **Notification** : Alertes CNIL en cas de violation < 72h

**Contraintes Opérationnelles**
- **Budget** : Infrastructure on-premise (pas de cloud)
- **Équipe** : 1-2 développeurs
- **Timeline** : 16 semaines de développement
- **Documentation** : Française et anglaise

---

## 2.2. Architecture Globale de la Plateforme

### 2.2.1. Architecture en Couches

Notre plateforme adopte une **architecture en 7 couches** pour séparer les responsabilités :

```
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE 7 : PRÉSENTATION                       │
│              Grafana Dashboards | Web UI | Mobile App            │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │ HTTP/WebSocket
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COUCHE 6 : API GATEWAY                        │
│           FastAPI REST | GraphQL | Authentication                │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐
│   COUCHE 5 : ANALYTIQUE      │  │   COUCHE 5' : CACHE          │
│  ML Models | Predictions     │  │   Redis | Memcached          │
│  Recommendations | Anomalies │  │   Hot Data | Session Store   │
└──────────────────────────────┘  └──────────────────────────────┘
                    ▲                           ▲
                    └─────────────┬─────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  COUCHE 4 : TRAITEMENT                           │
│         Apache Spark Streaming | Aggregations | ETL              │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  COUCHE 3 : MESSAGING                            │
│              Apache Kafka | Topics | Partitions                  │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   COUCHE 2 : COLLECTE                            │
│        Data Generators | IoT Connectors | APIs Externes          │
└─────────────────────────────────────────────────────────────────┘
                                  ▲
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   COUCHE 1 : STOCKAGE                            │
│   PostgreSQL (OLTP) | MongoDB (Logs) | MinIO (Objects)          │
└─────────────────────────────────────────────────────────────────┘
```

**Avantages de cette Architecture :**
1. **Séparation des préoccupations** : Chaque couche a une responsabilité unique
2. **Scalabilité indépendante** : Chaque couche peut scaler séparément
3. **Testabilité** : Tests unitaires par couche, tests d'intégration inter-couches
4. **Maintenabilité** : Modifications localisées, couplage faible
5. **Évolutivité** : Ajout de nouvelles fonctionnalités sans refonte globale

### 2.2.2. Pattern Lambda Architecture

Nous implémentons une **Lambda Architecture** pour combiner traitement batch et streaming :

```
                    ┌──────────────────────────────┐
                    │      Data Sources (IoT)       │
                    └──────────────┬────────────────┘
                                   │
                    ┌──────────────┴────────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────┐          ┌───────────────────┐
        │   BATCH LAYER     │          │  SPEED LAYER      │
        │ (Spark Batch)     │          │ (Spark Streaming) │
        │                   │          │                   │
        │ • Données hist.   │          │ • Temps réel      │
        │ • Entraînement ML │          │ • Latence < 1s    │
        │ • Agrégations     │          │ • Approximations  │
        │ • Précision max   │          │                   │
        └─────────┬─────────┘          └─────────┬─────────┘
                  │                              │
                  └──────────┬───────────────────┘
                             ▼
                 ┌───────────────────────┐
                 │   SERVING LAYER       │
                 │   (PostgreSQL +       │
                 │    Redis Cache)       │
                 │                       │
                 │ • Batch views         │
                 │ • Real-time views     │
                 │ • Query merging       │
                 └───────────────────────┘
                             │
                             ▼
                      ┌────────────┐
                      │  API REST  │
                      └────────────┘
```

**Batch Layer (Précision)**
- Traite l'intégralité des données historiques
- Entraînement des modèles ML toutes les 24h
- Agrégations complexes et exactes
- Latence acceptable (minutes/heures)

**Speed Layer (Latence)**
- Traite uniquement les nouvelles données
- Prédictions temps réel avec modèles pré-entraînés
- Agrégations approximatives (HyperLogLog, Count-Min Sketch)
- Latence minimale (< 1 seconde)

**Serving Layer (Requêtes)**
- Combine vues batch et vues temps réel
- Cache intelligent avec Redis
- Index optimisés pour requêtes rapides
- Matérialisation de vues

### 2.2.3. Modèle de Déploiement

**Architecture Microservices avec Docker Compose**

```yaml
# docker-compose.yml - Vue simplifiée
version: '3.8'

services:
  # Infrastructure
  zookeeper:         # Coordination Kafka
  kafka:             # Message broker
  
  # Storage
  postgres:          # Base relationnelle
  mongodb:           # Base NoSQL
  redis:             # Cache in-memory
  minio:             # Object storage (S3-like)
  
  # Processing
  spark-master:      # Orchestrateur Spark
  spark-worker:      # Nœuds de calcul
  
  # Application
  data-generator:    # Générateurs IoT
  ml-models-runner:  # Entraînement et inférence ML
  api:               # API REST FastAPI
  
  # Monitoring & Visualization
  grafana:           # Dashboards
  prometheus:        # Métriques (optionnel)
```

**Flux de Données End-to-End**

```
1. GÉNÉRATION
   Data Generator → Kafka Topics (7 topics)
   Fréquence: 5 secondes
   Format: JSON

2. INGESTION
   Kafka → Spark Streaming Consumer
   Micro-batches: 30 secondes
   Partitions: 3 par topic

3. TRAITEMENT
   Spark Streaming → Transformations + Agrégations
   Window: 5 minutes
   Détection anomalies: Temps réel

4. STOCKAGE
   Spark → PostgreSQL (données structurées)
   Spark → MongoDB (logs, documents)
   PostgreSQL → Redis (cache hot data)

5. ANALYTIQUE
   PostgreSQL → ML Models (Python)
   Entraînement: Toutes les 24h
   Inférence: < 200ms

6. API
   FastAPI → PostgreSQL + Redis
   Endpoints: 20+
   Cache hit rate: 67%

7. VISUALISATION
   Grafana → PostgreSQL (requêtes SQL)
   Dashboards: 6
   Refresh: 5-10 secondes
```

---

## 2.3. Conception Détaillée des Composants

### 2.3.1. Couche de Collecte - Data Generators

**7 Générateurs de Données Simulées**

```python
# Architecture modulaire des générateurs
class DataGenerator(ABC):
    """Interface abstraite pour tous les générateurs"""
    
    @abstractmethod
    def generate(self, timestamp: datetime) -> List[Dict]:
        """Génère les données pour un timestamp donné"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict:
        """Retourne le schéma JSON des données"""
        pass

# Implémentations concrètes
generators = {
    'traffic':    TrafficGenerator(),        # 19 capteurs
    'transport':  PublicTransportGenerator(), # 34 véhicules
    'parking':    ParkingGenerator(),         # 12 parkings
    'bikes':      BikeShareGenerator(),       # 24 stations
    'taxis':      TaxiGenerator(),            # 50 taxis/VTC
    'weather':    WeatherGenerator(),         # 1 station météo
    'pollution':  PollutionGenerator()        # 5 stations
}
```

**Génération avec Patterns Temporels**

```python
# Patterns réalistes de trafic
TRAFFIC_PATTERNS = {
    'morning_peak':  (7, 9,  1.8),  # 7-9h, multiplier x1.8
    'lunch':         (12, 13, 1.3),
    'evening_peak':  (17, 19, 2.0),  # 17-19h, multiplier x2.0
    'night':         (0, 5,   0.3),
    'weekend':       'all',   0.7)   # Samedi-Dimanche, x0.7
}

def apply_temporal_pattern(base_value, timestamp):
    """Applique le multiplicateur temporel"""
    hour = timestamp.hour
    dow = timestamp.dayofweek
    
    # Weekend reduction
    if dow in [5, 6]:
        base_value *= 0.7
    
    # Hourly pattern
    for pattern, (start, end, mult) in TRAFFIC_PATTERNS.items():
        if start <= hour <= end:
            base_value *= mult
            break
    
    # Random variation ±10%
    base_value *= random.uniform(0.9, 1.1)
    
    return base_value
```

### 2.3.2. Couche Messaging - Apache Kafka

**Configuration des Topics**

```python
KAFKA_TOPICS_CONFIG = {
    'traffic-sensors': {
        'partitions': 3,
        'replication_factor': 1,  # 3 en production
        'retention_ms': 86400000,  # 24h
        'compression_type': 'gzip'
    },
    'public-transport': {
        'partitions': 3,
        'replication_factor': 1,
        'retention_ms': 86400000,
        'compression_type': 'gzip'
    },
    # ... autres topics
}

# Stratégie de partitionnement
def partition_key(record: Dict, topic: str) -> str:
    """Clé de partitionnement pour distribution équilibrée"""
    if topic == 'traffic-sensors':
        return record['zone_id']  # Partitionnement par zone
    elif topic == 'public-transport':
        return record['line_id']  # Partitionnement par ligne
    else:
        return record['sensor_id']  # Par défaut
```

**Producteur Kafka Optimisé**

```python
producer = KafkaProducer(
    bootstrap_servers='kafka:9093',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    
    # Performance tuning
    acks='all',              # Attendre tous les brokers (durabilité)
    retries=3,               # 3 tentatives en cas d'échec
    max_in_flight_requests_per_connection=5,
    
    # Batching pour throughput
    batch_size=16384,        # 16KB
    linger_ms=10,            # Attendre 10ms pour remplir batch
    
    # Compression
    compression_type='gzip', # Réduction 60% de la bande passante
    
    # Buffers
    buffer_memory=33554432   # 32MB
)
```

### 2.3.3. Couche Traitement - Apache Spark Streaming

**Job Spark Structured Streaming**

```python
spark = SparkSession.builder \
    .appName("SmartCityStreaming") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "2g") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# Lire depuis Kafka
traffic_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9093") \
    .option("subscribe", "traffic-sensors") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parser le JSON
parsed_stream = traffic_stream \
    .selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), traffic_schema).alias("data")) \
    .select("data.*")

# Agrégations par fenêtres temporelles
windowed_traffic = parsed_stream \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("zone_id"),
        col("road_id")
    ) \
    .agg(
        avg("speed_kmh").alias("avg_speed"),
        sum("vehicle_flow").alias("total_flow"),
        avg("occupancy_percent").alias("avg_occupancy"),
        count("*").alias("sensor_count"),
        stddev("speed_kmh").alias("speed_stddev")
    )
```

**Détection d'Anomalies en Temps Réel**

```python
# UDF pour calculer le Z-score
@udf(returnType=DoubleType())
def calculate_zscore(value, mean, stddev):
    if stddev == 0:
        return 0.0
    return abs((value - mean) / stddev)

# Détecter anomalies (Z-score > 3)
anomalies = windowed_traffic \
    .withColumn("speed_zscore", 
                calculate_zscore(col("avg_speed"), 
                               lit(50),  # Moyenne historique
                               col("speed_stddev"))) \
    .filter(
        (col("speed_zscore") > 3) |         # Vitesse anormale
        (col("avg_speed") < 10) |            # Congestion sévère
        (col("avg_occupancy") > 95)          # Occupation critique
    ) \
    .withColumn("anomaly_type",
        when(col("avg_speed") < 10, "severe_congestion")
        .when(col("avg_occupancy") > 95, "critical_occupancy")
        .otherwise("statistical_outlier")
    ) \
    .withColumn("severity",
        when(col("speed_zscore") > 5, "critical")
        .when(col("speed_zscore") > 3, "high")
        .otherwise("medium")
    )
```

### 2.3.4. Couche Stockage - Modèle de Données

**Schéma PostgreSQL**

```sql
-- Table principale de trafic
CREATE TABLE traffic_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    road_id VARCHAR(20) NOT NULL,
    road_name VARCHAR(100),
    zone_id VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    speed_kmh DECIMAL(5, 2) CHECK (speed_kmh >= 0 AND speed_kmh <= 200),
    vehicle_flow INTEGER CHECK (vehicle_flow >= 0),
    occupancy_percent DECIMAL(5, 2) CHECK (occupancy_percent >= 0 AND occupancy_percent <= 100),
    congestion_level VARCHAR(20) CHECK (congestion_level IN ('low', 'medium', 'high')),
    data_quality VARCHAR(20) DEFAULT 'good',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_traffic_timestamp ON traffic_data(timestamp DESC);
CREATE INDEX idx_traffic_zone ON traffic_data(zone_id);
CREATE INDEX idx_traffic_sensor_time ON traffic_data(sensor_id, timestamp DESC);
CREATE INDEX idx_traffic_congestion ON traffic_data(congestion_level, timestamp DESC);

-- Partitionnement par mois (Time-Series Optimization)
CREATE TABLE traffic_data_2025_11 PARTITION OF traffic_data
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');
```

**Schéma MongoDB (Logs et Documents)**

```javascript
// Collection: system_logs
{
  _id: ObjectId("..."),
  timestamp: ISODate("2025-11-20T14:30:00Z"),
  service: "spark-streaming",
  level: "INFO",
  message: "Processed batch 1234",
  metadata: {
    batch_id: 1234,
    records_count: 39600,
    processing_time_ms: 382
  }
}

// Collection: ml_predictions
{
  _id: ObjectId("..."),
  sensor_id: "traffic-sensor-001",
  prediction_timestamp: ISODate("2025-11-20T15:00:00Z"),
  predicted_speed_kmh: 42.3,
  confidence: 0.88,
  model_version: "ensemble_v2.1",
  features_used: [...],
  horizon_minutes: 30
}

// Collection: user_queries (audit trail)
{
  _id: ObjectId("..."),
  user_id: "admin",
  endpoint: "/api/v1/predict/traffic",
  timestamp: ISODate("2025-11-20T14:32:15Z"),
  response_time_ms: 89,
  status_code: 200,
  cached: true
}
```

### 2.3.5. Couche Analytique - Modèles ML

**Architecture des Modèles**

```python
class ModelPipeline:
    """Pipeline complet d'entraînement et d'inférence"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models = {
            'xgboost': XGBoostModel(),
            'lstm': LSTMModel(),
            'transformer': TransformerModel()
        }
        self.ensemble = EnsembleModel(self.models)
    
    def train(self, df: pd.DataFrame):
        """Entraînement complet"""
        # 1. Feature engineering
        df_features = self.feature_engineer.transform(df)
        
        # 2. Split temporel (pas de shuffle)
        train, val, test = self.temporal_split(df_features, [0.7, 0.15, 0.15])
        
        # 3. Entraîner chaque modèle
        for name, model in self.models.items():
            print(f"Training {name}...")
            model.fit(train, val)
            metrics = model.evaluate(test)
            print(f"{name} Test MAE: {metrics['mae']:.2f}")
        
        # 4. Entraîner l'ensemble
        self.ensemble.fit(val)  # Optimiser les poids
        
        # 5. Sauvegarder
        self.save_all_models()
    
    def predict(self, df: pd.DataFrame, horizon_hours: int) -> Dict:
        """Prédiction avec ensemble"""
        df_features = self.feature_engineer.transform(df)
        return self.ensemble.predict(df_features, horizon_hours)
```

**Feature Engineering Avancé**

```python
class FeatureEngineer:
    """Création de features pour ML"""
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # 1. Features temporelles cycliques
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # 2. Lag features (observations passées)
        for lag in [1, 2, 3, 6, 12, 24]:
            df[f'speed_lag_{lag}'] = df.groupby('sensor_id')['speed_kmh'].shift(lag)
        
        # 3. Rolling statistics
        for window in [3, 6, 12, 24]:
            df[f'speed_ma_{window}'] = df.groupby('sensor_id')['speed_kmh'] \
                .transform(lambda x: x.rolling(window, min_periods=1).mean())
            df[f'speed_std_{window}'] = df.groupby('sensor_id')['speed_kmh'] \
                .transform(lambda x: x.rolling(window, min_periods=1).std())
        
        # 4. Historical patterns (même heure jours précédents)
        for days_back in [1, 7, 14, 28]:
            df[f'speed_same_hour_{days_back}d'] = df.groupby('sensor_id')['speed_kmh'] \
                .shift(days_back * 288)  # 288 = 24h * 12 (5min intervals)
        
        # 5. Interaction features
        df['speed_flow_interaction'] = df['speed_kmh'] * df['vehicle_flow']
        df['is_peak_weekend'] = df['is_rush_hour'] * df['is_weekend']
        
        return df.fillna(method='ffill').fillna(0)
```

---

**Ce chapitre présente l'analyse complète des besoins et l'architecture détaillée de la plateforme. Le chapitre suivant décrit l'implémentation technique.**
