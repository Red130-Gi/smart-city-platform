# Architecture de la Plateforme Smart City

## Vue d'Ensemble

La plateforme Smart City est une solution complète de gestion urbaine intelligente basée sur le Big Data et l'Intelligence Artificielle, conçue pour optimiser les services urbains avec un focus particulier sur la mobilité et le transport.

## Architecture Technique

### 1. Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                         COUCHE PRÉSENTATION                      │
├─────────────────────────────────────────────────────────────────┤
│                            Grafana                               │
│                   (Dashboards & Visualisation)                   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                          COUCHE API                              │
├─────────────────────────────────────────────────────────────────┤
│                         FastAPI REST                             │
│              (Traffic, Transport, Mobility, Analytics)           │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                     COUCHE TRAITEMENT                            │
├─────────────────────────────────────────────────────────────────┤
│     Apache Spark          │        Machine Learning              │
│  (Stream Processing)       │    (XGBoost, LSTM, Transformers)   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      COUCHE MESSAGING                            │
├─────────────────────────────────────────────────────────────────┤
│                         Apache Kafka                             │
│              (Topics: traffic, transport, incidents)             │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                      COUCHE DONNÉES                              │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL     │    MongoDB      │    Redis      │    MinIO    │
│  (Relationnel)  │    (NoSQL)      │   (Cache)     │  (Object)   │
└─────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCES DE DONNÉES                            │
├─────────────────────────────────────────────────────────────────┤
│   Capteurs IoT  │  GPS Véhicules  │  APIs Externes │  Météo     │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Composants Principaux

#### 2.1 Collecte de Données
- **Générateurs IoT simulés** : Production de données en temps réel
- **Formats supportés** : JSON, CSV, API REST
- **Fréquence** : 5 secondes pour les données temps réel

#### 2.2 Pipeline de Traitement
- **Kafka** : Message broker pour le streaming
  - Topics : traffic-sensors, public-transport, taxi-vtc, parking, bike-share, incidents, weather, air-quality
- **Spark Streaming** : Traitement des flux en temps réel
  - Agrégations temporelles (fenêtres de 5 minutes)
  - Détection d'anomalies
  - Calcul d'indices de mobilité

#### 2.3 Stockage
- **PostgreSQL** : Données structurées et historiques
- **MongoDB** : Données semi-structurées et documents
- **Redis** : Cache et données temps réel
- **MinIO** : Stockage objet compatible S3

#### 2.4 Machine Learning
- **Modèles de prédiction** :
  - XGBoost : Prédiction de trafic court terme
  - LSTM : Prédiction de séries temporelles
  - Transformer : Prédiction avancée multi-horizons
- **Détection d'anomalies** :
  - Isolation Forest
  - Autoencoders
  - DBSCAN pour clustering spatial

#### 2.5 API REST
- **FastAPI** : Framework moderne et performant
- **Endpoints** :
  - `/traffic` : Données et prédictions de trafic
  - `/transport` : Informations transport public
  - `/mobility` : Services de mobilité multimodale
  - `/incidents` : Gestion des incidents
  - `/analytics` : Analyses et KPIs

#### 2.6 Visualisation
- **Grafana** : Tableaux de bord interactifs
  - Dashboard Overview : Vue d'ensemble du système
  - Dashboard Traffic : Gestion du trafic
  - Dashboard Mobility : Transport et mobilité
  - Alertes automatiques

### 3. Flux de Données

```
1. Génération → 2. Kafka → 3. Spark → 4. Stockage → 5. API → 6. Grafana
     ↓              ↓           ↓          ↓            ↓         ↓
   IoT/GPS      Messages    Streaming   DB/Cache    REST API   Dashboards
```

### 4. Scalabilité

#### Horizontale
- Kafka : Ajout de brokers et partitions
- Spark : Ajout de workers
- API : Load balancing avec plusieurs instances
- Bases de données : Réplication et sharding

#### Verticale
- Augmentation des ressources (CPU, RAM)
- Optimisation des configurations Spark
- Tuning des bases de données

### 5. Sécurité

#### Authentification & Autorisation
- JWT tokens pour l'API
- RBAC dans Grafana
- SSL/TLS pour les communications

#### Protection des Données
- Chiffrement au repos (databases)
- Chiffrement en transit (TLS)
- Anonymisation des données personnelles

### 6. Monitoring & Observabilité

- **Prometheus** : Métriques système
- **Grafana** : Visualisation des métriques
- **Logs** : Centralisés dans ElasticSearch
- **Alerting** : Règles dans Grafana

### 7. Déploiement

#### Docker Compose
```yaml
services:
  - kafka & zookeeper
  - spark-master & workers
  - postgresql & mongodb
  - redis & minio
  - api
  - data-generator
  - grafana
```

#### Kubernetes (Production)
- Helm charts pour le déploiement
- HPA pour l'auto-scaling
- PVC pour le stockage persistant

### 8. Performance

#### Objectifs
- Latence API : < 500ms (P95)
- Throughput : 100k requêtes/min
- Disponibilité : 99.9%
- Processing lag : < 1 minute

#### Optimisations
- Caching avec Redis
- Index sur PostgreSQL
- Partitioning dans Kafka
- Spark tuning

### 9. Points d'Extension

- **Nouveaux types de capteurs** : Ajout simple via nouveaux topics Kafka
- **Nouveaux modèles ML** : Architecture modulaire dans ml-models/
- **Nouvelles visualisations** : Dashboards Grafana personnalisables
- **APIs tierces** : Intégration via connecteurs

### 10. Maintenance

#### Backup & Recovery
- Backup automatique des BDD
- Snapshots MinIO
- Export des configurations Grafana

#### Mise à jour
- Rolling updates pour zero-downtime
- Versioning des APIs
- Migration des schémas de BDD
