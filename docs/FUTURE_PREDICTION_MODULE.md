# Module de Prédiction Future du Trafic - Documentation

## Vue d'ensemble

Cette documentation décrit la nouvelle fonctionnalité de prédiction future du trafic pour la plateforme Smart City. Le système permet de prédire les conditions de circulation dans le futur (jusqu'à 7 jours) et de recommander des itinéraires alternatifs en fonction des prévisions.

## Architecture du Système

### Composants Principaux

1. **Module ML de Prédiction Future** (`ml-models/future_prediction.py`)
   - Modèles utilisés : LSTM, XGBoost, Prophet
   - Prédiction multi-horizon (1h, 3h, 6h, 12h, 1j, 3j, 7j)
   - Ensemble learning pour améliorer la précision

2. **Système de Recommandation d'Itinéraires** (`ml-models/route_recommendation.py`)
   - Algorithme de recherche de chemins multiples
   - Scoring basé sur les prédictions futures
   - Prise en compte des préférences utilisateur

3. **API REST** (`api/routers/prediction.py`)
   - Nouveaux endpoints pour la prédiction et les recommandations
   - Cache Redis pour optimiser les performances
   - Documentation Swagger automatique

4. **Traitement Batch Spark** (`data-pipeline/batch_processing.py`)
   - Préparation des données historiques
   - Entraînement des modèles
   - Génération de prédictions en lot

## API Endpoints

### 1. Prédiction de Trafic Future

#### Endpoint Simple (GET)
```
GET /api/v1/predict/traffic?road=X&datetime=2024-01-15T13:00:00
```

**Paramètres:**
- `road` (string, requis): Identifiant de la route/capteur
- `datetime` (string, requis): Date/heure cible au format ISO

**Réponse:**
```json
{
  "road": "road-1",
  "datetime": "2024-01-15T13:00:00",
  "prediction": {
    "speed_kmh": 35.5,
    "congestion": "medium",
    "confidence": 0.82
  },
  "status": "success"
}
```

#### Endpoint Avancé (POST)
```
POST /api/v1/predict/future
```

**Corps de la requête:**
```json
{
  "road": "road-1",
  "datetime": "2024-01-15T13:00:00"
}
```

**Réponse:**
```json
{
  "road_id": "road-1",
  "target_datetime": "2024-01-15T13:00:00",
  "predicted_speed_kmh": 35.5,
  "predicted_flow": 120,
  "predicted_density": 45,
  "congestion_level": "medium",
  "confidence": 0.82,
  "prediction_horizon_hours": 2.5,
  "model_used": "ensemble",
  "alternatives": ["alt_road-1_1", "alt_road-1_2"]
}
```

### 2. Recommandation d'Itinéraires

#### Endpoint Simple (GET)
```
GET /api/v1/recommend/route?origin=48.8566,2.3522&destination=48.8606,2.3376&datetime=2024-01-15T13:00:00
```

**Paramètres:**
- `origin` (string, requis): Coordonnées d'origine (lat,lon)
- `destination` (string, requis): Coordonnées de destination (lat,lon)
- `datetime` (string, requis): Heure de départ prévue

**Réponse:**
```json
{
  "origin": "48.8566,2.3522",
  "destination": "48.8606,2.3376",
  "datetime": "2024-01-15T13:00:00",
  "routes": [
    {
      "route_id": "route_1",
      "distance_km": 5.2,
      "duration_minutes": 15,
      "congestion": "medium",
      "reason": "Primary route"
    },
    {
      "route_id": "route_2",
      "distance_km": 6.8,
      "duration_minutes": 12,
      "congestion": "light",
      "reason": "Faster travel time"
    }
  ],
  "status": "success"
}
```

#### Endpoint Avancé (POST)
```
POST /api/v1/recommend/routes
```

**Corps de la requête:**
```json
{
  "origin_lat": 48.8566,
  "origin_lon": 2.3522,
  "destination_lat": 48.8606,
  "destination_lon": 2.3376,
  "datetime": "2024-01-15T13:00:00",
  "max_routes": 3,
  "preferences": {
    "avoid_highways": false,
    "prefer_scenic": true
  }
}
```

### 3. Prévisions sur Horizon Temporel

```
GET /api/v1/forecast/{road_id}?hours=24&interval=1
```

**Paramètres:**
- `road_id` (string, requis): Identifiant de la route
- `hours` (int, optionnel): Horizon de prévision en heures (défaut: 24, max: 168)
- `interval` (int, optionnel): Intervalle entre prédictions en heures (défaut: 1)

**Réponse:**
```json
{
  "road_id": "road-1",
  "forecast_start": "2024-01-15T10:00:00",
  "forecast_hours": 24,
  "interval_hours": 1,
  "predictions": [
    {
      "datetime": "2024-01-15T11:00:00",
      "hours_ahead": 1,
      "predicted_speed_kmh": 45.2,
      "congestion_level": "low",
      "confidence": 0.92
    },
    ...
  ]
}
```

## Modèles de Machine Learning

### 1. LSTM (Long Short-Term Memory)

**Architecture:**
- Couches LSTM empilées (128, 64, 32 neurones)
- Mécanisme d'attention
- Sorties multiples pour différents horizons temporels
- Dropout pour la régularisation

**Caractéristiques:**
- Capture les dépendances temporelles longues
- Excellent pour les patterns répétitifs (heures de pointe)
- Meilleure précision pour les prédictions court-terme (< 6h)

### 2. XGBoost

**Configuration:**
- 200 arbres de décision
- Profondeur maximale: 8
- Learning rate: 0.05
- Modèles séparés pour chaque horizon

**Caractéristiques:**
- Rapide pour l'inférence
- Bonne gestion des features catégorielles
- Performant sur les prédictions moyen-terme (6-24h)

### 3. Prophet

**Configuration:**
- Saisonnalités: journalière, hebdomadaire, mensuelle, annuelle
- Prise en compte des jours fériés
- Ajustement automatique des changements de tendance

**Caractéristiques:**
- Excellent pour les prédictions long-terme (> 24h)
- Gestion native des données manquantes
- Quantification de l'incertitude

### Ensemble Learning

Les prédictions finales sont calculées par une moyenne pondérée des trois modèles, avec des poids basés sur:
- La confiance de chaque modèle
- L'horizon de prédiction
- Les performances historiques

## Features Engineering

### Features Temporelles

1. **Basiques:**
   - Heure, minute, jour de la semaine
   - Jour du mois, mois, année
   - Semaine de l'année, trimestre

2. **Encodage Cyclique:**
   - Sin/Cos pour heure (période 24h)
   - Sin/Cos pour jour de la semaine (période 7j)
   - Sin/Cos pour mois (période 12m)

3. **Indicateurs Binaires:**
   - Weekend (samedi/dimanche)
   - Jours fériés
   - Heures de pointe (7-9h, 17-19h)
   - Périodes de la journée

### Features Historiques

1. **Lag Features:**
   - Vitesse à t-1, t-2, t-3, t-6, t-12 (5min à 1h)
   - Flux de véhicules décalés
   - Taux d'occupation décalés

2. **Patterns Historiques:**
   - Même heure jours précédents (1, 7, 14, 28 jours)
   - Même jour de la semaine semaines précédentes
   - Moyennes mensuelles par heure
   - Moyennes par jour de la semaine et heure

3. **Statistiques Roulantes:**
   - Moyenne mobile (15min, 1h)
   - Écart-type roulant
   - Somme du flux sur fenêtres temporelles

## Système de Recommandation d'Itinéraires

### Algorithme de Base

1. **Construction du Graphe Routier:**
   - Nœuds: intersections
   - Arêtes: segments de route
   - Poids: distance, temps prévu, congestion

2. **Recherche de Chemins:**
   - K plus courts chemins (Dijkstra/A*)
   - Chemins alternatifs par variation des poids
   - Filtrage par préférences utilisateur

3. **Scoring des Routes:**
   ```
   Score = α * congestion + β * duration + γ * distance
   ```
   Où α=0.4, β=0.4, γ=0.2 (paramètres ajustables)

### Critères de Sélection

1. **Congestion Prévue:**
   - Basée sur les prédictions futures
   - Agrégée sur tous les segments de la route

2. **Temps de Trajet:**
   - Calculé segment par segment
   - Ajusté selon la vitesse prédite

3. **Distance Totale:**
   - Somme des longueurs de segments
   - Pénalité pour les détours importants

4. **Préférences Utilisateur:**
   - Éviter autoroutes
   - Préférer routes panoramiques
   - Minimiser les péages (futur)

## Configuration Docker

### Services Mis à Jour

```yaml
ml-models-runner:
  build: ./ml-models
  environment:
    - MONGODB_URL=mongodb://admin:smartcity123@mongodb:27017
    - REDIS_URL=redis://redis:6379
    - FORECAST_HORIZON_HOURS=168
    - MODEL_TYPE=ensemble
    - ENABLE_FUTURE_PREDICTION=true
  volumes:
    - ./ml-models:/app
    - ./models:/models
    - ./data:/data
```

### Nouvelles Dépendances

- `prophet==1.1.5`: Prédictions séries temporelles
- `networkx==3.1`: Algorithmes de graphe
- `geopy==2.4.0`: Calculs géospatiaux

## Pipeline de Données

### Traitement Batch (Spark)

1. **Préparation des Données:**
   - Extraction des features temporelles
   - Calcul des statistiques historiques
   - Agrégation par capteur/route

2. **Entraînement des Modèles:**
   - Division train/test temporelle
   - Validation croisée sur séries temporelles
   - Sauvegarde des modèles entraînés

3. **Génération de Prédictions:**
   - Batch predictions pour tous les capteurs
   - Horizons multiples
   - Stockage dans MongoDB

### Flux Temps Réel

1. **Collecte:** Kafka → Spark Streaming
2. **Enrichissement:** Ajout features temps réel
3. **Prédiction:** Inférence avec modèles pré-entraînés
4. **Stockage:** MongoDB + Cache Redis
5. **API:** FastAPI avec cache

## Métriques de Performance

### Métriques ML

1. **MAE (Mean Absolute Error):** < 5 km/h
2. **RMSE (Root Mean Square Error):** < 7 km/h
3. **R² Score:** > 0.75
4. **Confiance moyenne:** > 80%

### Métriques Système

1. **Latence API:** < 200ms (p95)
2. **Taux de cache:** > 60%
3. **Throughput:** > 1000 req/s
4. **Disponibilité:** > 99.9%

## Dashboard Grafana

### Panneaux Principaux

1. **Prévision de Vitesse:** Graphique temporel multi-routes
2. **Niveau de Congestion:** Statistiques par niveau
3. **Confiance des Prédictions:** Gauge horizontal
4. **Heatmap Horaire:** Distribution des prédictions
5. **Recommandations de Routes:** Table avec métriques
6. **Performance des Modèles:** MAE en temps réel
7. **Distribution des Horizons:** Répartition des prédictions
8. **Temps de Réponse API:** Monitoring des endpoints

### Variables du Dashboard

- `$road`: Sélection multiple de routes
- Rafraîchissement automatique: 30 secondes
- Période par défaut: 6 dernières heures

## Déploiement

### Prérequis

1. Docker & Docker Compose
2. 8GB RAM minimum
3. 20GB espace disque
4. Ports: 8000 (API), 3000 (Grafana), 9092 (Kafka)

### Installation

```bash
# Cloner le repository
git clone https://github.com/your-org/smart-city-platform

# Lancer les services
docker-compose up -d

# Vérifier les logs
docker-compose logs -f ml-models-runner

# Accéder à l'API
curl http://localhost:8000/api/v1/predict/traffic?road=road-1&datetime=2024-01-15T13:00:00
```

### Configuration

Variables d'environnement importantes:
- `MODEL_TYPE`: Type de modèle (lstm, xgboost, prophet, ensemble)
- `FORECAST_HORIZON_HOURS`: Horizon maximal en heures
- `ENABLE_FUTURE_PREDICTION`: Activer les prédictions futures

## Exemples d'Utilisation

### Python
```python
import requests
from datetime import datetime, timedelta

# Prédiction future
response = requests.get(
    "http://localhost:8000/api/v1/predict/traffic",
    params={
        "road": "road-1",
        "datetime": (datetime.now() + timedelta(hours=3)).isoformat()
    }
)
prediction = response.json()
print(f"Vitesse prévue: {prediction['prediction']['speed_kmh']} km/h")

# Recommandation d'itinéraire
response = requests.post(
    "http://localhost:8000/api/v1/recommend/routes",
    json={
        "origin_lat": 48.8566,
        "origin_lon": 2.3522,
        "destination_lat": 48.8606,
        "destination_lon": 2.3376,
        "datetime": datetime.now().isoformat(),
        "max_routes": 3
    }
)
routes = response.json()
for route in routes['routes']:
    print(f"Route {route['route_id']}: {route['duration_minutes']} min")
```

### JavaScript
```javascript
// Prédiction future
fetch('http://localhost:8000/api/v1/predict/traffic?' + new URLSearchParams({
    road: 'road-1',
    datetime: new Date(Date.now() + 3*60*60*1000).toISOString()
}))
.then(res => res.json())
.then(data => {
    console.log(`Vitesse prévue: ${data.prediction.speed_kmh} km/h`);
});

// Recommandation d'itinéraire
fetch('http://localhost:8000/api/v1/recommend/routes', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        origin_lat: 48.8566,
        origin_lon: 2.3522,
        destination_lat: 48.8606,
        destination_lon: 2.3376,
        datetime: new Date().toISOString(),
        max_routes: 3
    })
})
.then(res => res.json())
.then(data => {
    data.routes.forEach(route => {
        console.log(`Route ${route.route_id}: ${route.duration_minutes} min`);
    });
});
```

## Maintenance et Monitoring

### Logs Importants

```bash
# Logs du modèle ML
docker logs ml-models-runner

# Logs de l'API
docker logs smart-city-api

# Métriques Spark
docker logs spark-master
```

### Réentraînement des Modèles

Le réentraînement est automatique toutes les 24h, mais peut être déclenché manuellement:

```bash
docker exec ml-models-runner python /app/run_pipeline.py --train
```

### Sauvegarde des Modèles

Les modèles sont sauvegardés dans `/models/saved/`:
- `lstm_model.h5`: Modèle LSTM
- `xgboost_*.pkl`: Modèles XGBoost par horizon
- `prophet_*.pkl`: Modèles Prophet par route
- `scalers.pkl`: Normalisateurs de données

## Améliorations Futures

1. **Intégration de données externes:**
   - Météo (impact sur le trafic)
   - Événements (concerts, matchs)
   - Travaux routiers

2. **Optimisations:**
   - Modèles spécifiques par zone
   - Auto-tuning des hyperparamètres
   - Compression des modèles

3. **Nouvelles fonctionnalités:**
   - Prédiction multi-modale (voiture + transports publics)
   - Optimisation de flotte
   - Alertes prédictives

4. **Amélioration de l'interface:**
   - Application mobile
   - Notifications push
   - Intégration GPS

## Support et Contact

Pour toute question ou problème:
- Documentation API: http://localhost:8000/docs
- Dashboard Grafana: http://localhost:3000
- Issues GitHub: https://github.com/your-org/smart-city-platform/issues

---

*Documentation mise à jour le: Novembre 2024*
*Version: 2.0.0*
