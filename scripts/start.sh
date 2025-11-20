#!/bin/bash

# Smart City Platform - Script de démarrage
echo "========================================="
echo "   Smart City Platform - Démarrage"
echo "========================================="

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker Desktop."
    exit 1
fi

# Vérifier Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

echo "✅ Docker et Docker Compose détectés"

# Créer les répertoires nécessaires
echo "📁 Création des répertoires..."
mkdir -p grafana/provisioning/dashboards/json
mkdir -p data/kafka
mkdir -p data/mongodb
mkdir -p data/postgres

# Démarrer les services de base
echo "🚀 Démarrage des services de base..."
docker-compose up -d zookeeper kafka mongodb postgres redis minio

# Attendre que les services soient prêts
echo "⏳ Attente de l'initialisation des services (30s)..."
sleep 30

# Démarrer Spark
echo "🎯 Démarrage de Spark..."
docker-compose up -d spark-master spark-worker

# Attendre Spark
sleep 10

# Démarrer Grafana
echo "📊 Démarrage de Grafana..."
docker-compose up -d grafana

# Démarrer l'API
echo "🌐 Démarrage de l'API..."
docker-compose up -d api

# Attendre l'API
sleep 10

# Démarrer le générateur de données
echo "📡 Démarrage du générateur de données..."
docker-compose up -d data-generator

echo ""
echo "========================================="
echo "✨ Smart City Platform démarrée !"
echo "========================================="
echo ""
echo "🔗 URLs d'accès:"
echo "   - Grafana:        http://localhost:3000"
echo "     User: admin / Pass: smartcity123"
echo "   - API:            http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - Spark UI:       http://localhost:8080"
echo "   - MinIO Console:  http://localhost:9001"
echo ""
echo "📝 Logs:"
echo "   docker-compose logs -f [service]"
echo ""
echo "🛑 Pour arrêter:"
echo "   ./scripts/stop.sh"
echo "========================================="
