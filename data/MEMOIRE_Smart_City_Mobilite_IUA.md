# Mémoire de Master – Institut Universitaire d'Abidjan

## Conception d’une plateforme intelligente de services urbains basée sur le Big Data et l’Intelligence Artificielle

Sous-thème: Mobilité et transport urbain (trafic, bus, taxi, optimisation des trajets)

Étudiant: [À compléter]

Encadrant académique: [À compléter]

Encadrant professionnel: [À compléter]

Filière: Master en Génie Informatique – Option [À compléter]

Année académique: 2024–2025

---

## Remerciements

[À compléter]

---

## Dédicace (facultatif)

[À compléter]

---

## Résumé

Ce mémoire présente la conception et la réalisation d’une plateforme intelligente de services urbains, focalisée sur la mobilité et le transport (trafic routier, bus, taxis, optimisation des trajets) pour une ville intelligente. S’appuyant sur une architecture distribuée hybride, la solution intègre un pipeline de traitement temps réel (Kafka + Spark Structured Streaming), un socle de stockage (PostgreSQL, MongoDB, Redis), des modèles d’IA (XGBoost, LSTM, Transformers) pour la prédiction, et des tableaux de bord Grafana pour la visualisation opérationnelle. La plateforme vise à améliorer l’analyse des flux de mobilité, l’anticipation des congestions et l’aide à la décision.

Mots-clés: Smart City, Mobilité, Big Data, Streaming, IA, Kafka, Spark, Grafana.

---

## Abstract

This thesis presents the design and implementation of an intelligent urban services platform focusing on mobility and transport (road traffic, buses, taxis, route optimization) for smart cities. The system relies on a hybrid distributed architecture with real-time streaming (Kafka + Spark Structured Streaming), a multi-model storage layer (PostgreSQL, MongoDB, Redis), AI models (XGBoost, LSTM, Transformers) for traffic prediction, and Grafana dashboards for operational visualization. The proposed platform enhances mobility analytics, congestion forecasting, and decision support.

Keywords: Smart City, Mobility, Big Data, Streaming, AI, Kafka, Spark, Grafana.

---

## Liste des figures

- Figure 1 – Architecture globale de la plateforme Smart City (Mobilité)
- Figure 2 – Pipeline temps réel Kafka/Spark
- Figure 3 – Schéma des données de trafic et transport public
- Figure 4 – Modèle d’apprentissage (XGBoost/LSTM) pour la prédiction de vitesse
- Figure 5 – Dashboards Grafana (vue d’ensemble, trafic, mobilité)

## Liste des tableaux

- Tableau 1 – Technologies et rôles dans l’architecture
- Tableau 2 – Indicateurs clés de performance (KPIs)
- Tableau 3 – Jeux de données simulés (capteurs et attributs)
- Tableau 4 – Résultats expérimentaux (latence, précision, robustesse)

---

## Table des matières

- Introduction générale
- PARTIE I – Cadre général du stage et du projet
  - Chapitre 1: Présentation du cadre du stage
  - Chapitre 2: Cahier des charges du projet
- PARTIE II – Cadre théorique et conceptuel
  - Chapitre 3: Revue de littérature et état de l’art
  - Chapitre 4: Méthodologie et conception générale
- PARTIE III – Réalisation, expérimentation et analyse
  - Chapitre 5: Conception détaillée et mise en œuvre
  - Chapitre 6: Tests, validation et résultats
- PARTIE IV – Évaluation, perspectives et conclusion
  - Chapitre 7: Évaluation globale du projet
  - Conclusion générale
- Références bibliographiques
- Annexes

---

# Introduction générale

## Contexte et justification
La croissance urbaine des métropoles africaines, notamment Abidjan, entraîne des défis majeurs de mobilité: congestion chronique, manque de visibilité en temps réel, coordination limitée entre modes (bus, taxis, VTC, vélos), et difficultés d’anticipation. Les approches modernes basées sur le Big Data et l’IA offrent la capacité d’intégrer et d’analyser des flux massifs et hétérogènes pour améliorer la planification, l’exploitation et l’information voyageur. 

## Problématique
Comment concevoir une plateforme intelligente capable d’intégrer, analyser et exploiter efficacement les données massives des infrastructures urbaines afin d’améliorer la qualité des services de mobilité (trafic, transport public, taxis, optimisation de trajets) dans le contexte d’une Smart City?

## Objectif général
Concevoir et mettre en œuvre une plateforme de mobilité urbaine intelligente, temps réel, scalable et visualisable, centrée sur l’aide à la décision.

## Objectifs spécifiques
- Intégrer des données IoT simulées: capteurs trafic, bus, taxis, parkings, vélos, météo, incidents.
- Traiter en temps réel via Kafka + Spark Streaming, avec agrégations glissantes (fenêtres de 5–15 min).
- Développer des modèles IA pour prédire vitesse/flux et détecter des anomalies.
- Offrir des tableaux de bord opérationnels uniquement via Grafana.
- Définir un cadre de gouvernance (qualité, sécurité, conformité).

## Méthodologie générale
- Architecture distribuée conteneurisée (Docker Compose; extensible Kubernetes).
- Pipeline de streaming (Kafka/Spark), socle données (PostgreSQL, MongoDB, Redis), visualisation Grafana.
- Expérimentation sur données simulées; évaluation de la latence, précision, robustesse.

## Organisation du mémoire
Le mémoire est structuré en quatre parties: contexte et cahier des charges; état de l’art et méthodologie; réalisation et résultats; évaluation et perspectives.

---

# PARTIE I – Cadre général du stage et du projet

## Chapitre 1 – Présentation du cadre du stage

### 1.1 Organisme d’accueil
- Institut Universitaire d’Abidjan (IUA) – établissement d’enseignement supérieur.
- Partenariats envisagés: collectivités, opérateurs de transport, intégrateurs.

### 1.2 Environnement technique et professionnel
- Infrastructures: environnement de développement local (Windows), conteneurs Docker.
- Outils: Git, FastAPI, Kafka, Spark, MongoDB, PostgreSQL, Redis, MinIO, Grafana.

### 1.3 Intégration du stagiaire
- Missions: conception, implémentation, expérimentation d’une plateforme Mobilité.
- Encadrement: un encadrant académique (IUA) et un encadrant technique.

## Chapitre 2 – Cahier des charges du projet

### 2.1 Contexte et justification
- Besoin d’une vision unifiée et temps réel des conditions de mobilité.
- Anticipation des congestions pour optimiser l’offre (bus), l’information, et la régulation.

### 2.2 Objectifs
- Généraux: plateforme modulaire, temps réel, visualisation opérationnelle.
- Spécifiques: intégration de multiples flux, prédictions court terme (5–60 min), optimisation de routes.

### 2.3 Analyse du besoin
- Acteurs: opérateurs (SOTRA, taxis), autorités, DSI municipale, citoyens.
- Exigences: faible latence (< 1 min pour agrégations), haute disponibilité, scalabilité horizontale.
- Contraintes: hétérogénéité des données, qualité/fiabilité, confidentialité.

### 2.4 Spécifications
- Fonctionnelles: collecte/traitement, prédictions, alertes, tableaux de bord Grafana.
- Techniques: Kafka topics, Spark Structured Streaming, bases PostgreSQL/MongoDB, API REST.

### 2.5 Moyens et ressources
- Docker Compose (démo); possibilité de Helm/Kubernetes (prod).
- GPU optionnel pour LSTM/Transformer; CPU suffisant pour POC.

### 2.6 Planification
- Étapes: design, génération de données, pipeline streaming, IA, API, dashboards, tests.

### 2.7 Indicateurs de succès
- Latence, précision MAE/RMSE, disponibilité, couverture fonctionnelle, UX des dashboards.

---

# PARTIE II – Cadre théorique et conceptuel

## Chapitre 3 – Revue de littérature et état de l’art

### 3.1 Concepts clés
- Smart City: intégration de capteurs, analytics et services.
- Big Data/Streaming: ingestion continue, traitement événementiel, fenêtres glissantes.
- IA pour mobilité: séries temporelles, détection anomalies, optimisation multi-objectifs.

### 3.2 Solutions existantes
- Plateformes open-source (Kafka, Spark, Grafana) largement adoptées pour la télémétrie.
- Suites propriétaires orientées ITS; coût/fermeture limitant l’adaptabilité locale.

### 3.3 Analyse critique
- Points forts: écosystème mature, intégration facilitée, temps réel fiable.
- Limites: dépendance à la qualité des capteurs, coût d’exploitation à l’échelle, gouvernance.

### 3.4 Cadre conceptuel
- Schéma: Sources → Kafka → Spark → Stockage → API → Grafana.
- Modèles prédictifs: XGBoost (features tabulaires), LSTM/Transformer (séquences).

## Chapitre 4 – Méthodologie et conception générale

### 4.1 Démarche
- Développement itératif (Agile) avec incréments validés (POC → MVP).

### 4.2 Processus de réalisation
- Génération de données, pipeline streaming, feature engineering, entraînement, exposé via API, dashboards.

### 4.3 Choix technologiques
- Kafka + Spark: robuste pour streaming à faible latence.
- PostgreSQL + MongoDB + Redis: polyglotte et performant.
- Grafana: visualisation unique (pas de front-end React sur demande).

### 4.4 Modélisation
- Schémas de données trafic/transport (capteurs, positions, incidents, lignes bus).
- Architecture logique: microservices (API), couches données, streaming, analytics, visu.

---

# PARTIE III – Réalisation, expérimentation et analyse

## Chapitre 5 – Conception détaillée et mise en œuvre

### 5.1 Architecture
- Conteneurs: Kafka/Zookeeper, Spark (master/worker), PostgreSQL, MongoDB, Redis, MinIO, API, Data-Generator, Grafana.
- Réseau Docker isolé; volumes pour persistance.

### 5.2 Données et ingestion
- Flux simulés: trafic routier (vitesse, débit, occupation), bus (GPS, passagers, retards), taxis (disponibilité), parking, vélos, incidents, météo.
- Kafka topics dédiés: traffic-sensors, public-transport, incidents, etc.

### 5.3 Traitement temps réel
- Spark Structured Streaming: agrégations par fenêtres (5/10/15 min), watermarks, détection d’anomalies (vitesse<5 km/h, sur-occupation).
- Calcul d’indices: congestion_score, punctuality_score, mobility_index.

### 5.4 Couches IA/ML
- Features: décalages (lag), moyennes glissantes, EWM, indicateurs de congestion.
- Modèles: XGBoost/LightGBM (tabulaire), LSTM/Transformer (séquentiel) pour vitesse/flux; autoencoder/anomalies.

### 5.5 API et visualisation
- API FastAPI: endpoints incidents/analytics (mock et intégrables).
- Grafana: provisioning datasources (PostgreSQL, MongoDB, API) et dashboards (overview/traffic/mobility) sans React.

## Chapitre 6 – Tests, validation et résultats

### 6.1 Méthodologie de test
- Tests unitaires de transformations; tests d’intégration pipeline; tests charge/laten ce.
- Jeux de données synthétiques contrôlées.

### 6.2 Indicateurs et métriques
- Latence (P95) du pipeline < 60 s; disponibilité; throughput messages; MAE/RMSE prédictions; utilisation CPU/RAM.

### 6.3 Résultats (POC)
- Pipeline démarré via Docker Compose; dashboards Grafana provisionnés.
- Exemples cibles: MAE(LSTM) ~ [à mesurer]; Latence streaming ~ [à mesurer]; Ponctualité bus ~ [simulé].

### 6.4 Analyse
- Le couplage Kafka/Spark offre des garanties de scalabilité et de résilience.
- La précision dépend de la richesse des features et de la qualité capteurs.

---

# PARTIE IV – Évaluation, perspectives et conclusion

## Chapitre 7 – Évaluation globale du projet

### 7.1 Évaluation technique/fonctionnelle
- Objectifs atteints: pipeline temps réel, IA, visualisation Grafana, API; architecture modulaire.

### 7.2 Impacts
- Aide à la décision pour opérateurs; amélioration potentielle de la régulation et information.

### 7.3 Limites
- Données simulées; besoin d’intégration capteurs réels et tarification/contrats.

### 7.4 Recommandations
- Passage Kubernetes; intégration GTFS-RT; normalisation DATEX II; ajout de graphes routiers (OSM) et algorithmes multi-objectifs; expérimentations en conditions réelles à Abidjan.

## Conclusion générale

Ce travail propose une plateforme de mobilité urbaine s’appuyant sur le Big Data et l’IA, intégrant ingestion temps réel, traitement analytique, modèles prédictifs et visualisation opérationnelle exclusivement avec Grafana. Les résultats préliminaires montrent la faisabilité et l’intérêt opérationnel. Les perspectives portent sur l’industrialisation (Kubernetes), l’intégration de données réelles et l’enrichissement des modèles.

---

# Références bibliographiques (sélection)

- Apache Kafka – Documentation officielle. https://kafka.apache.org/
- Apache Spark – Structured Streaming Guide. https://spark.apache.org/structured-streaming/
- Grafana – Documentation. https://grafana.com/docs/
- FastAPI – Documentation. https://fastapi.tiangolo.com/
- PostgreSQL – Documentation. https://www.postgresql.org/docs/
- MongoDB – Documentation. https://www.mongodb.com/docs/
- G. Box, G. Jenkins, Time Series Analysis: Forecasting and Control, 2015.
- S. Hochreiter, J. Schmidhuber, Long Short-Term Memory, Neural Computation, 1997.
- T. Chen, C. Guestrin, XGBoost: A Scalable Tree Boosting System, KDD 2016.
- A. Vaswani et al., Attention Is All You Need, NeurIPS 2017.

---

# Annexes

## Annexe A – Schéma d’architecture (répertoire du projet)
- docker-compose.yml: orchestration des services.
- data-pipeline/spark_streaming.py: traitement streaming.
- ml-models/traffic_prediction.py: prédiction trafic et anomalies.
- grafana/provisioning/: datasources et dashboards.
- api/: endpoints FastAPI (incidents, analytics).

## Annexe B – Indicateurs et formules
- Congestion_score: f(vitesse moyenne par tronçon).
- MAE, RMSE pour évaluer les modèles.

## Annexe C – Guide de démarrage rapide
- cf. QUICKSTART.md.

[Fin du document]
