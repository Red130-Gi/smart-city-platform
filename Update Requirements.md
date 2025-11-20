Objectif :
Mettre à jour le projet Smart City pour ajouter un système de prédiction FUTURE des congestions routières et proposer des itinéraires alternatifs.

Contexte existant :

Sources de données : Kafka → Spark Streaming → Stockage (Data Lake / Warehouse) → API → Grafana

Modèle utilisé : LSTM / XGBoost

Le pipeline actuel permet uniquement la prédiction en temps réel.

Nouvelle fonctionnalité à implémenter :

Le modèle doit être capable de prédire la congestion dans le futur, par exemple :

prédire l’état d’une voie X le mardi prochain à 13h ;

fournir une prévision horaire (forecast) pour les prochaines heures / prochains jours.

Le système doit permettre à un utilisateur d’indiquer :

une date/heure de passage prévue ;

une voie souhaitée.

Le modèle doit :

prédire la congestion sur cette voie à l’heure demandée ;

si congestion probable, proposer une autre voie alternative moins saturée, en comparant :

taux de trafic prévu,

vitesse moyenne,

densité des véhicules,

historique des congestions.

L’API doit être mise à jour avec les endpoints suivants :

GET /predict/traffic?road=X&datetime=...

GET /recommend/route?origin=...&destination=...&datetime=...

Le pipeline doit être modifié pour inclure :

un module de prévision future (forecast) basé sur :

LSTM multivariate

ou Prophet

ou XGBoost + features temporelles

un module de recommandation d’itinéraire basé sur un scoring :

congestion prévue

vitesse prévue

historique

distance

Le code attendu :

architecture Docker/Kubernetes mise à jour ;

nouveau module ML ;

entraînement ;

API complète ;

ajustements Spark Streaming / batch processing ;

interface Grafana pour visualiser les prévisions futures ;

documentation.

Livrables attendus :

Code complet

Docker-compose 

code ML

Code Python Spark

API (FastAPI ou Flask)

Documentation markdown