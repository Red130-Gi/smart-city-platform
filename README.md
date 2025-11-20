# 🏙️ Smart City Platform - Plateforme Intelligente de Services Urbains

## 📋 Description

Plateforme intelligente basée sur le Big Data et l'Intelligence Artificielle pour l'optimisation des services urbains dans le contexte des villes intelligentes (Smart Cities), avec un focus particulier sur la mobilité et le transport.

## 🎯 Objectifs Principaux

### Mobilité & Transport
- **Prévision de trafic** : Prédiction des niveaux de congestion et temps de trajet
- **Optimisation multimodale** : Recommandations personnalisées pour bus, métro, vélo, taxi
- **Gestion de flottes** : Amélioration de la ponctualité des transports publics
- **Sécurité** : Détection d'anomalies et alertes précoces
- **Durabilité** : Réduction de l'empreinte carbone

## 🏗️ Architecture

### Composants Principaux
- **Data Collection** : Simulateurs IoT et collecte de données urbaines
- **Data Lake** : Stockage structuré (Raw/Staging/Curated)
- **Stream Processing** : Kafka + Spark Streaming
- **ML Pipeline** : Modèles de prédiction et optimisation
- **API Services** : Services REST pour applications
- **Visualisation** : Dashboards Grafana temps réel
- **Orchestration** : Docker/Kubernetes

## 📁 Structure du Projet

```
smart-city-platform/
├── api/                    # API REST FastAPI
├── data-generation/        # Génération de données IoT simulées
├── data-pipeline/          # Pipeline Spark de traitement
├── ml-models/              # Modèles d'IA et ML
├── grafana/                # Configuration et dashboards Grafana
│   ├── provisioning/       # Datasources et dashboards
│   └── grafana.ini         # Configuration Grafana
├── scripts/                # Scripts de démarrage/arrêt
├── docs/                   # Documentation technique
└── docker-compose.yml      # Orchestration des services
```

## 🚀 Technologies Utilisées

### Infrastructure
- Docker & Kubernetes
- Apache Kafka
- Apache Spark
- MongoDB / PostgreSQL

### Machine Learning
- XGBoost
- LSTM / Transformers
- Scikit-learn
- TensorFlow / PyTorch

### Visualisation
- Grafana

### API & Backend
- FastAPI
- Redis

## 📊 Métriques Clés

- **Latence** : < 500ms pour les prédictions temps réel
- **Précision** : > 85% pour les prévisions de trafic
- **Disponibilité** : 99.9% SLA
- **Scalabilité** : Support de 100k+ requêtes/min

## 🔧 Installation

### Prérequis
- Docker Desktop
- Python 3.9+ (optionnel, pour scripts ML)
- 16GB RAM minimum

### Installation rapide (Windows)
```bash
# Naviguer vers le dossier du projet
cd c:\Users\wind7\CascadeProjects\smart-city-platform

# Lancer l'infrastructure avec Docker
docker-compose up -d

# Ou utiliser le script de démarrage
scripts\start.bat
```

### Accès aux services
- **Grafana** : http://localhost:3000 (admin/smartcity123)
- **API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

## 📚 Documentation

- [Architecture Technique](docs/architecture.md)
- [Guide API](docs/api-guide.md)
- [Modèles ML](docs/ml-models.md)
- [Gouvernance des Données](docs/governance.md)

## 📈 Roadmap

- ✅ Phase 1 : Infrastructure de base
- ✅ Phase 2 : Pipeline de données
- 🚧 Phase 3 : Modèles ML
- 📅 Phase 4 : Dashboards Grafana
- 📅 Phase 5 : Extension multi-sectorielle

## 👥 Contributeurs

Plateforme développée dans le cadre du projet Smart City Initiative.

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.
