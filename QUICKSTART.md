# 🚀 Guide de Démarrage Rapide - Smart City Platform

## Prérequis

- **Docker Desktop** installé et en cours d'exécution
- **8 GB RAM** minimum (16 GB recommandé)
- **20 GB** d'espace disque disponible
- Ports libres: 3000, 5432, 6379, 8000, 8080, 9000, 9001, 9092, 27017

## Installation Rapide (Windows)

### 1. Cloner ou extraire le projet
```bash
cd c:\Users\wind7\CascadeProjects\smart-city-platform
```

### 2. Démarrer la plateforme
Double-cliquez sur:
```
scripts\start.bat
```

Ou en ligne de commande:
```bash
docker-compose up -d
```

### 3. Attendre l'initialisation (2-3 minutes)

### 4. Accéder aux services

## 🌐 URLs d'Accès

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** (Visualisation) | http://localhost:3000 | admin / smartcity123 |
| **API REST** | http://localhost:8000 | - |
| **API Documentation** | http://localhost:8000/docs | - |
| **Spark UI** | http://localhost:8080 | - |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin123 |

## 📊 Dashboards Grafana

Une fois connecté à Grafana:

1. **Vue d'ensemble** : Smart City - Vue d'Ensemble
   - Métriques globales
   - KPIs principaux
   - Alertes actives

2. **Gestion du Trafic** : Smart City - Gestion du Trafic
   - Carte temps réel
   - Heatmap de congestion
   - Prédictions

3. **Mobilité** : Smart City - Mobilité et Transport
   - Transport public
   - Vélos partagés
   - Parking

## 🔧 Commandes Utiles

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f grafana
docker-compose logs -f api
docker-compose logs -f data-generator
```

### Statut des services
```bash
docker-compose ps
```

### Arrêter la plateforme
```bash
scripts\stop.bat
# ou
docker-compose down
```

### Redémarrer un service
```bash
docker-compose restart grafana
docker-compose restart api
```

## 📡 Test de l'API

### Vérifier la santé
```bash
curl http://localhost:8000/health
```

### Obtenir les données de trafic
```bash
curl http://localhost:8000/api/v1/traffic/current
```

### Obtenir les statistiques
```bash
curl http://localhost:8000/api/v1/stats
```

## 🎯 Cas d'Usage

### 1. Visualiser le trafic en temps réel
1. Ouvrir Grafana
2. Aller sur "Smart City - Gestion du Trafic"
3. Observer la carte et les métriques

### 2. Analyser la mobilité urbaine
1. Dashboard "Smart City - Mobilité et Transport"
2. Voir la répartition modale
3. Analyser les tendances

### 3. Gérer les incidents
1. API: `GET /api/v1/incidents/active`
2. Visualiser sur les dashboards
3. Recevoir des alertes

## 🚨 Dépannage

### Docker ne démarre pas
```bash
# Vérifier Docker
docker version

# Redémarrer Docker Desktop
```

### Port déjà utilisé
```bash
# Identifier le processus
netstat -ano | findstr :3000

# Modifier le port dans docker-compose.yml
```

### Pas de données dans Grafana
```bash
# Vérifier le générateur
docker-compose logs data-generator

# Redémarrer le générateur
docker-compose restart data-generator
```

### Erreur de connexion à la base
```bash
# Vérifier PostgreSQL
docker-compose logs postgres

# Réinitialiser
docker-compose down -v
docker-compose up -d
```

## 📈 Architecture Simplifiée

```
Données IoT → Kafka → Spark → Bases de données → API → Grafana
     ↓           ↓        ↓            ↓            ↓        ↓
Génération   Streaming  Analyse   Stockage    Services  Visualisation
```

## 🔄 Workflow Typique

1. **Génération** : Les capteurs IoT simulés génèrent des données
2. **Streaming** : Kafka transmet les données
3. **Traitement** : Spark analyse en temps réel
4. **Stockage** : PostgreSQL/MongoDB persistent
5. **API** : Services REST exposent les données
6. **Visualisation** : Grafana affiche les dashboards

## 🎓 Pour Aller Plus Loin

- [Architecture Technique](docs/architecture.md)
- [Gouvernance des Données](docs/governance.md)
- [Documentation API](http://localhost:8000/docs)
- [Configuration Grafana](grafana/README.md)

## 💡 Tips

1. **Performance** : Allouer plus de RAM à Docker Desktop
2. **Développement** : Modifier les fichiers et redémarrer les services
3. **Production** : Utiliser Kubernetes pour le déploiement

## 📞 Support

En cas de problème:
1. Vérifier les logs: `docker-compose logs -f [service]`
2. Consulter la documentation
3. Redémarrer les services: `docker-compose restart`

## ✅ Checklist de Validation

- [ ] Docker Desktop en cours d'exécution
- [ ] Tous les services démarrés (`docker-compose ps`)
- [ ] Grafana accessible (http://localhost:3000)
- [ ] API répond (http://localhost:8000/health)
- [ ] Données générées (vérifier logs data-generator)
- [ ] Dashboards affichent des données

Félicitations ! Votre plateforme Smart City est opérationnelle ! 🎉
