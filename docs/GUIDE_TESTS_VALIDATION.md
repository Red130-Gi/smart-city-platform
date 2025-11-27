# 🧪 Guide de Tests et Validation - Smart City Platform

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Prérequis](#prérequis)
3. [Tests d'Infrastructure](#tests-dinfrastructure)
4. [Tests de Base de Données](#tests-de-base-de-données)
5. [Tests Big Data](#tests-big-data)
6. [Tests Machine Learning](#tests-machine-learning)
7. [Tests API](#tests-api)
8. [Tests Dashboards](#tests-dashboards)
9. [Validation Complète](#validation-complète)
10. [Interprétation des Résultats](#interprétation-des-résultats)

---

## 🎯 Vue d'ensemble

Ce guide décrit la procédure complète de tests et validation de la plateforme Smart City. Il couvre tous les composants du système depuis l'infrastructure jusqu'aux dashboards.

### Objectifs de la Validation

- ✅ Vérifier que tous les services sont opérationnels
- ✅ Valider l'intégrité des données
- ✅ Tester les pipelines Big Data
- ✅ Vérifier la précision des modèles ML
- ✅ Confirmer l'accessibilité des API
- ✅ Valider les visualisations Grafana

---

## 🔧 Prérequis

### Logiciels Requis

```bash
# Docker Desktop
docker --version
# Docker version 24.0.0 ou supérieur

# Docker Compose
docker-compose --version
# Docker Compose version 2.0.0 ou supérieur

# Python
python --version
# Python 3.8 ou supérieur

# Dépendances Python
pip install psycopg2-binary pymongo requests kafka-python
```

### Services à Démarrer

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Attendre 30-60 secondes pour l'initialisation complète
```

---

## 🐳 Tests d'Infrastructure

### Test 1: Vérification des Containers Docker

**Commande:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Services attendus:**
- ✅ smart-city-postgres (Port 5432)
- ✅ smart-city-mongodb (Port 27017)
- ✅ smart-city-redis (Port 6379)
- ✅ smart-city-kafka (Port 9092)
- ✅ smart-city-zookeeper (Port 2181)
- ✅ smart-city-spark (Ports 4040, 7077)
- ✅ smart-city-grafana (Port 3000)
- ✅ smart-city-api (Port 8000)

**Critères de succès:**
- Au moins 7/8 services actifs
- Status "Up" pour tous les services critiques

### Test 2: Santé des Containers

**Commande:**
```bash
# Vérifier les logs de chaque service
docker logs --tail 50 smart-city-postgres
docker logs --tail 50 smart-city-mongodb
docker logs --tail 50 smart-city-kafka
docker logs --tail 50 smart-city-spark
```

**Critères de succès:**
- Aucune erreur critique dans les logs
- Messages de démarrage réussi visibles
- Pas de redémarrages en boucle

---

## 🗄️ Tests de Base de Données

### Test 3: PostgreSQL - Validation Complète

**Script automatisé:**
```bash
# Exécuter le script de validation SQL
docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -f /tests/validate_database.sql
```

**Tests manuels:**
```sql
-- Connexion
docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb

-- Test 1: Lister les tables
\dt

-- Test 2: Compter les données
SELECT COUNT(*) FROM traffic_data;
SELECT COUNT(*) FROM predictions;
SELECT COUNT(*) FROM zones;
SELECT COUNT(*) FROM taxi_trips;

-- Test 3: Données récentes
SELECT COUNT(*) FROM traffic_data 
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Test 4: Statistiques de base
SELECT 
    zone_id,
    COUNT(*) as records,
    AVG(speed_kmh) as avg_speed,
    AVG(vehicle_count) as avg_vehicles
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY zone_id;
```

**Critères de succès:**
- ✅ Toutes les tables principales existent
- ✅ Au moins 1000 enregistrements dans `traffic_data`
- ✅ Données récentes (< 1 heure)
- ✅ Toutes les 5 zones ont des données
- ✅ Pas de valeurs NULL dans les colonnes critiques

### Test 4: MongoDB - Validation

**Commande:**
```bash
# Connexion MongoDB
docker exec -it smart-city-mongodb mongosh

# Dans le shell MongoDB:
use smartcity
show collections
db.realtime_events.count()
db.traffic_aggregates.count()
db.ml_results.count()
```

**Critères de succès:**
- ✅ Collections créées
- ✅ Documents présents dans les collections
- ✅ Index créés correctement

---

## ⚡ Tests Big Data

### Test 5: Apache Spark - Pipeline de Streaming

**Script Python automatisé:**
```bash
python tests/validate_bigdata.py
```

**Tests manuels:**

```bash
# Vérifier le container Spark
docker ps | grep spark

# Consulter les logs Spark
docker logs --tail 100 smart-city-spark

# Vérifier les jobs actifs
curl http://localhost:4040/api/v1/applications
```

**Critères de succès:**
- ✅ Container Spark actif
- ✅ Spark Context initialisé
- ✅ Streaming en cours d'exécution
- ✅ Pas d'exceptions dans les logs
- ✅ Traitement des batches visible

### Test 6: Kafka - Messages et Topics

**Commande:**
```bash
# Lister les topics
docker exec smart-city-kafka kafka-topics --list --bootstrap-server localhost:9092

# Consommer des messages (test)
docker exec smart-city-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic traffic-events \
  --max-messages 5 \
  --from-beginning
```

**Topics attendus:**
- `traffic-events`
- `predictions`
- `anomalies`
- `alerts`

**Critères de succès:**
- ✅ Tous les topics créés
- ✅ Messages présents dans les topics
- ✅ Format JSON valide
- ✅ Pas de lag excessif

---

## 🧠 Tests Machine Learning

### Test 7: Modèles ML - Prédictions

**Script Python automatisé:**
```bash
python tests/test_predictions_ml.py
```

**Tests API manuels:**

```bash
# Test 1: Prédictions futures
curl "http://localhost:8000/api/v1/predict/traffic/future?zone_id=zone-1&horizon_hours=24"

# Test 2: Prédictions multi-zones
curl "http://localhost:8000/api/v1/predict/traffic/multizone?zones=zone-1,zone-2,zone-3"

# Test 3: Route optimale
curl "http://localhost:8000/api/v1/predict/route/optimal?origin_zone=zone-1&destination_zone=zone-3"

# Test 4: Détection d'anomalies
curl "http://localhost:8000/api/v1/predict/anomalies?zone_id=all"
```

**Critères de succès:**
- ✅ API répond en < 2 secondes
- ✅ Prédictions cohérentes (vitesse entre 0-100 km/h)
- ✅ Score de confiance > 0.7
- ✅ Tous les horizons disponibles (1h, 6h, 12h, 24h)
- ✅ Format JSON valide

### Test 8: Qualité des Modèles

**Métriques à vérifier:**

```python
# Dans l'API ou logs ML
# - Accuracy: > 80%
# - RMSE: < 10 km/h
# - MAE: < 5 km/h
# - R² Score: > 0.75
```

**Validation:**
```sql
-- Comparer prédictions vs réalité
SELECT 
    p.zone_id,
    p.predicted_speed,
    t.speed_kmh as actual_speed,
    ABS(p.predicted_speed - t.speed_kmh) as error
FROM predictions p
JOIN traffic_data t ON 
    p.zone_id = t.zone_id AND 
    p.prediction_time = t.timestamp
WHERE p.prediction_time > NOW() - INTERVAL '1 hour'
ORDER BY error DESC
LIMIT 20;
```

---

## 🔌 Tests API

### Test 9: Endpoints API

**Health Check:**
```bash
curl http://localhost:8000/health
# Réponse attendue: {"status": "healthy"}
```

**Documentation Interactive:**
```
http://localhost:8000/docs
```

**Tous les Endpoints:**

| Endpoint | Méthode | Description | Test |
|----------|---------|-------------|------|
| `/health` | GET | Santé de l'API | ✅ |
| `/api/v1/zones` | GET | Liste des zones | ✅ |
| `/api/v1/traffic/current` | GET | Trafic actuel | ✅ |
| `/api/v1/traffic/history` | GET | Historique | ✅ |
| `/api/v1/predict/traffic/future` | GET | Prédictions | ✅ |
| `/api/v1/predict/traffic/multizone` | GET | Multi-zones | ✅ |
| `/api/v1/predict/route/optimal` | GET | Route optimale | ✅ |
| `/api/v1/predict/anomalies` | GET | Anomalies | ✅ |

**Test de Performance:**
```bash
# Test de charge (nécessite Apache Bench)
ab -n 1000 -c 10 http://localhost:8000/api/v1/zones

# Critères:
# - Latence moyenne < 100ms
# - 99% des requêtes < 500ms
# - Aucune erreur 500
```

---

## 📊 Tests Dashboards

### Test 10: Grafana - Accessibilité

**Accès Web:**
```
http://localhost:3000
Login: admin
Password: admin
```

**Tests via API:**
```bash
# Health check
curl http://localhost:3000/api/health

# Liste des dashboards
curl -u admin:admin http://localhost:3000/api/search?type=dash-db

# Test d'une datasource
curl -u admin:admin http://localhost:3000/api/datasources
```

### Test 11: Dashboards - Données

**Dashboards à vérifier:**

1. **01 - Overview Production**
   - ✅ Métriques temps réel affichées
   - ✅ Graphiques actualisés
   - ✅ Pas de "No Data"

2. **02 - Traffic Production**
   - ✅ Cartes de chaleur fonctionnelles
   - ✅ Vitesses par zone
   - ✅ Niveaux de congestion

3. **03 - Predictions Production**
   - ✅ Prédictions multi-horizons
   - ✅ Graphiques de tendances
   - ✅ Scores de confiance

4. **04 - Real Data Dashboard**
   - ✅ Données taxis en temps réel
   - ✅ Trajets visualisés
   - ✅ Statistiques jour/nuit

**Script de validation:**
```bash
python scripts/check_grafana_data.bat
```

---

## 🔬 Validation Complète

### Exécution de Tous les Tests

**Script Automatisé Principal:**
```bash
# Windows
run_complete_validation.bat

# Ou manuellement:
python tests/comprehensive_validation.py
```

**Ce script vérifie:**
1. ✅ Infrastructure Docker (8 services)
2. ✅ PostgreSQL (tables, données, intégrité)
3. ✅ MongoDB (collections, documents)
4. ✅ Big Data (Spark, Kafka)
5. ✅ Machine Learning (modèles, prédictions)
6. ✅ API (endpoints, performance)
7. ✅ Grafana (dashboards, données)

**Durée estimée:** 5-10 minutes

---

## 📈 Interprétation des Résultats

### Rapports Générés

Après validation, consultez les rapports:

```
docs/
├── VALIDATION_REPORT.md          # Rapport principal (lisible)
├── VALIDATION_REPORT.json        # Données détaillées
└── BIGDATA_VALIDATION_REPORT.json # Spécifique Big Data
```

### Statuts Possibles

#### ✅ PASS (≥ 80% de réussite)
**Interprétation:** Plateforme opérationnelle et prête pour la production.

**Actions:**
- Aucune action immédiate requise
- Continuer le monitoring régulier
- Planifier des tests de charge si nécessaire

#### ⚠️ PARTIAL (50-79% de réussite)
**Interprétation:** Plateforme partiellement fonctionnelle avec des problèmes mineurs.

**Actions prioritaires:**
1. Identifier les composants en échec
2. Consulter les logs des services problématiques
3. Redémarrer les services si nécessaire
4. Vérifier les configurations
5. Relancer les tests

#### ❌ FAIL (< 50% de réussite)
**Interprétation:** Problèmes critiques nécessitant une intervention.

**Actions urgentes:**
1. Vérifier que Docker Desktop fonctionne
2. Vérifier les ressources système (RAM, CPU, disque)
3. Reconstruire les images: `docker-compose build --no-cache`
4. Supprimer les volumes: `docker-compose down -v`
5. Redémarrer complètement: `docker-compose up -d`
6. Consulter les logs détaillés

### Métriques Clés

| Composant | Métrique | Valeur Attendue | Critique |
|-----------|----------|-----------------|----------|
| PostgreSQL | Enregistrements | > 1000 | Oui |
| PostgreSQL | Données récentes | < 5 min | Oui |
| Spark | Batches traités | > 0 | Oui |
| Kafka | Messages/sec | > 10 | Non |
| ML Models | Accuracy | > 80% | Oui |
| API | Latence | < 200ms | Non |
| API | Uptime | > 99% | Oui |
| Grafana | Dashboards | = 4 | Non |

---

## 🔍 Troubleshooting

### Problème: Docker ne démarre pas

**Solution:**
```bash
# Windows
# 1. Ouvrir Docker Desktop
# 2. Settings > Resources > Augmenter RAM/CPU
# 3. Redémarrer Docker Desktop
```

### Problème: Services ne démarrent pas

**Solution:**
```bash
# Voir les logs
docker-compose logs [service]

# Redémarrer un service
docker-compose restart [service]

# Reconstruire
docker-compose build --no-cache [service]
docker-compose up -d
```

### Problème: Base de données vide

**Solution:**
```bash
# Relancer la génération de données
python data-generation/abidjan_data_generator.py

# Ou via script
scripts/activate_abidjan.bat
```

### Problème: API ne répond pas

**Solution:**
```bash
# Vérifier les logs API
docker logs smart-city-api

# Redémarrer
docker-compose restart api

# Tester en local
cd api
python -m uvicorn main:app --reload
```

### Problème: Grafana sans données

**Solution:**
```bash
# Vérifier les datasources
scripts/check_grafana_data.bat

# Re-importer les dashboards
docker-compose restart grafana
```

---

## 📚 Références

### Documentation
- [Architecture du Système](./architecture.md)
- [Guide Big Data](./SPARK_STREAMING_ACTIVATION.md)
- [Guide ML](./ML_PRODUCTION_ACTIVATION.md)
- [Guide Kubernetes](./KUBERNETES_DEPLOYMENT_GUIDE.md)

### Scripts Utiles
```bash
# Démarrage rapide
docker-compose up -d

# Arrêt
docker-compose down

# Logs en temps réel
docker-compose logs -f

# Nettoyage complet
docker-compose down -v
docker system prune -a
```

### Commandes de Debug

```bash
# Statistiques des containers
docker stats

# Inspecter un container
docker inspect smart-city-postgres

# Exécuter une commande dans un container
docker exec -it smart-city-postgres bash

# Voir les réseaux
docker network ls
docker network inspect smart-city-platform_default
```

---

## ✅ Checklist de Validation

Avant de considérer la plateforme comme validée, cochez:

- [ ] Tous les services Docker démarrés
- [ ] PostgreSQL accessible avec données récentes
- [ ] MongoDB opérationnel
- [ ] Spark traite les données en streaming
- [ ] Kafka reçoit et distribue les messages
- [ ] Modèles ML génèrent des prédictions cohérentes
- [ ] API répond à tous les endpoints
- [ ] Grafana affiche tous les dashboards
- [ ] Rapports de validation générés
- [ ] Taux de réussite ≥ 80%
- [ ] Aucune erreur critique dans les logs
- [ ] Performance acceptable (latence < 200ms)

---

## 🎓 Pour la Soutenance

### Points à Valider Avant la Soutenance

1. **Démonstration en Direct**
   - [ ] Tous les services fonctionnent
   - [ ] Dashboards actualisés en temps réel
   - [ ] API répond rapidement
   - [ ] Prédictions ML visibles

2. **Résultats à Présenter**
   - [ ] Rapport de validation complet
   - [ ] Métriques de performance
   - [ ] Graphiques de précision ML
   - [ ] Captures d'écran des dashboards

3. **Scénarios de Test**
   - [ ] Prédiction de trafic en temps réel
   - [ ] Détection d'anomalie
   - [ ] Recommandation de route
   - [ ] Analyse multi-zones

---

**Document maintenu par:** Smart City Platform Team  
**Dernière mise à jour:** 2024  
**Version:** 1.0
