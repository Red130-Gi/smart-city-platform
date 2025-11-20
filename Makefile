.PHONY: help start stop restart logs clean build status

help: ## Afficher cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Démarrer tous les services
	@echo "Démarrage de la plateforme Smart City..."
	docker-compose up -d
	@echo "Plateforme démarrée ! Accédez à Grafana sur http://localhost:3000"

stop: ## Arrêter tous les services
	@echo "Arrêt de la plateforme..."
	docker-compose down
	@echo "Plateforme arrêtée"

restart: stop start ## Redémarrer tous les services

logs: ## Afficher les logs de tous les services
	docker-compose logs -f

logs-api: ## Afficher les logs de l'API
	docker-compose logs -f api

logs-kafka: ## Afficher les logs de Kafka
	docker-compose logs -f kafka

logs-generator: ## Afficher les logs du générateur de données
	docker-compose logs -f data-generator

build: ## Reconstruire les images Docker
	docker-compose build --no-cache

clean: ## Nettoyer les volumes Docker (ATTENTION: supprime les données)
	docker-compose down -v
	@echo "Volumes supprimés"

status: ## Afficher le statut des services
	docker-compose ps

grafana-restart: ## Redémarrer Grafana uniquement
	docker-compose restart grafana

api-restart: ## Redémarrer l'API uniquement
	docker-compose restart api

spark-submit: ## Soumettre le job Spark de streaming
	docker exec spark-master spark-submit \
		--master spark://spark-master:7077 \
		--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 \
		/opt/spark-apps/spark_streaming.py

train-ml: ## Lancer l'entraînement des modèles ML
	cd ml-models && python traffic_prediction.py

test-api: ## Tester l'API
	curl http://localhost:8000/health

open-grafana: ## Ouvrir Grafana dans le navigateur
	@echo "Ouverture de Grafana..."
	@start http://localhost:3000 2>NUL || open http://localhost:3000 2>NUL || xdg-open http://localhost:3000 2>NUL

open-api: ## Ouvrir la documentation API
	@echo "Ouverture de l'API..."
	@start http://localhost:8000/docs 2>NUL || open http://localhost:8000/docs 2>NUL || xdg-open http://localhost:8000/docs 2>NUL

backup: ## Sauvegarder les données et configurations
	@echo "Sauvegarde en cours..."
	@mkdir -p backups
	docker exec postgres pg_dump -U smart_city smart_city_db > backups/postgres_backup_$$(date +%Y%m%d_%H%M%S).sql
	docker exec mongodb mongodump --out /backup
	docker cp mongodb:/backup backups/mongodb_backup_$$(date +%Y%m%d_%H%M%S)
	@echo "Sauvegarde terminée dans le dossier backups/"

monitor: ## Lancer le monitoring en temps réel
	@echo "Monitoring des ressources Docker..."
	docker stats
