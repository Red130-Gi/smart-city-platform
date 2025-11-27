# 🧪 Tests et Validation - Smart City Platform

## 📁 Contenu du Dossier

Ce dossier contient tous les scripts de tests et de validation de la plateforme.

### Scripts de Test

| Script | Description | Durée | Utilisation |
|--------|-------------|-------|-------------|
| `comprehensive_validation.py` | Validation complète tous composants | 5-10 min | `python tests/comprehensive_validation.py` |
| `test_predictions_ml.py` | Tests des prédictions ML via API | 2-3 min | `python tests/test_predictions_ml.py` |
| `validate_database.sql` | Validation SQL PostgreSQL | 1-2 min | `docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -f /tests/validate_database.sql` |
| `validate_bigdata.py` | Validation Spark et Kafka | 3-5 min | `python tests/validate_bigdata.py` |
| `generate_performance_report.py` | Génération graphiques performance | 1 min | `python tests/generate_performance_report.py` |
| `test_grafana_data.sql` | Tests données Grafana | 1 min | SQL via PostgreSQL |

## 🚀 Démarrage Rapide

### Prérequis

1. **Docker Desktop** en cours d'exécution
2. **Services démarrés:**
   ```bash
   docker-compose up -d
   ```

3. **Dépendances Python:**
   ```bash
   pip install psycopg2-binary pymongo requests matplotlib seaborn numpy
   ```

### Exécution Complète

**Windows:**
```bash
cd c:\memoire\smart-city-platform
run_complete_validation.bat
```

**Python Direct:**
```bash
python tests/comprehensive_validation.py
```

## 📊 Scripts Détaillés

### 1. comprehensive_validation.py

**Description:** Script principal de validation complète

**Tests effectués:**
- ✅ Infrastructure Docker (8 services)
- ✅ PostgreSQL (tables, données, intégrité)
- ✅ MongoDB (collections, documents)
- ✅ Spark Streaming (batches, performance)
- ✅ Kafka (topics, messages)
- ✅ Machine Learning (prédictions, précision)
- ✅ API REST (endpoints, latence)
- ✅ Grafana (dashboards, données)

**Sorties:**
- `docs/VALIDATION_REPORT.json` - Données brutes
- `docs/VALIDATION_REPORT.md` - Rapport lisible

**Exemple:**
```python
python tests/comprehensive_validation.py
# Résultat: 45/48 tests réussis (94%)
```

### 2. test_predictions_ml.py

**Description:** Tests spécifiques des prédictions ML

**Tests inclus:**
- Prédictions futures (multi-horizons)
- Prédictions multi-zones
- Recommandations de routes
- Détection d'anomalies
- Performance API
- Informations modèles

**Exemple:**
```python
python tests/test_predictions_ml.py
# Teste tous les endpoints ML
# Affiche précision, confiance, latence
```

### 3. validate_database.sql

**Description:** Validation complète PostgreSQL

**12 Tests SQL:**
1. Tables existantes
2. Nombre d'enregistrements
3. Données de trafic
4. Zones configurées
5. Prédictions ML
6. Données taxis
7. Qualité données (NULL)
8. Distribution temporelle
9. Top zones par activité
10. Index et contraintes
11. Statistiques performance
12. Résumé validation

**Exemple:**
```bash
docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -f /tests/validate_database.sql
```

### 4. validate_bigdata.py

**Description:** Validation Big Data (Spark + Kafka)

**Vérifications:**
- Container Spark actif
- Logs Spark (erreurs, processing)
- Topics Kafka
- Messages Kafka
- Jobs Streaming
- Traitement données
- Métriques Spark

**Sortie:**
- `docs/BIGDATA_VALIDATION_REPORT.json`

**Exemple:**
```python
python tests/validate_bigdata.py
# Statut Spark: ✅ Opérationnel
# Kafka Lag: 0
```

### 5. generate_performance_report.py

**Description:** Génère graphiques pour présentation

**Graphiques créés:**
1. `ml_accuracy_chart.png` - Précision ML par horizon
2. `zone_performance_chart.png` - Performance par zone
3. `api_latency_chart.png` - Latence endpoints
4. `error_distribution.png` - Distribution erreurs
5. `system_resources.png` - Utilisation ressources
6. `traffic_heatmap.png` - Carte chaleur trafic
7. `validation_summary.png` - Résumé tests
8. `performance_metrics.json` - Métriques JSON

**Exemple:**
```python
python tests/generate_performance_report.py
# Génère 8 fichiers dans docs/
```

## 📈 Interprétation des Résultats

### Codes de Sortie

| Statut | Signification | Action |
|--------|---------------|--------|
| ✅ PASS | ≥ 80% tests réussis | Aucune action |
| ⚠️ PARTIAL | 50-79% tests réussis | Vérifier logs |
| ❌ FAIL | < 50% tests réussis | Debug urgent |

### Métriques Clés

**Infrastructure:**
- Services actifs: 8/8 → ✅
- Services actifs: 5-7/8 → ⚠️
- Services actifs: < 5/8 → ❌

**Base de Données:**
- Données récentes (< 5 min) → ✅
- Données récentes (< 30 min) → ⚠️
- Pas de données récentes → ❌

**Machine Learning:**
- Précision > 85% → ✅
- Précision 75-85% → ⚠️
- Précision < 75% → ❌

**API:**
- Latence < 200ms → ✅
- Latence 200-500ms → ⚠️
- Latence > 500ms → ❌

## 🔍 Troubleshooting

### Problème: Docker non accessible

**Erreur:**
```
error during connect: Get "http://...": Le fichier spécifié est introuvable
```

**Solution:**
```bash
1. Ouvrir Docker Desktop
2. Attendre que Docker soit complètement chargé
3. Relancer les tests
```

### Problème: Import Error Python

**Erreur:**
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
```bash
pip install psycopg2-binary pymongo requests
```

### Problème: Services non démarrés

**Erreur:**
```
Connection refused
```

**Solution:**
```bash
# Démarrer les services
docker-compose up -d

# Attendre 60 secondes
timeout /t 60

# Relancer les tests
```

### Problème: PostgreSQL vide

**Erreur:**
```
SELECT COUNT(*) FROM traffic_data;
-- Retourne 0
```

**Solution:**
```bash
# Lancer la génération de données
python data-generation/abidjan_data_generator.py

# Ou utiliser le script
scripts/activate_abidjan.bat
```

## 📊 Rapports Générés

### Fichiers de Sortie

Après exécution des tests, les fichiers suivants sont créés dans `docs/`:

```
docs/
├── VALIDATION_REPORT.md           # Rapport principal (Markdown)
├── VALIDATION_REPORT.json         # Données validation (JSON)
├── BIGDATA_VALIDATION_REPORT.json # Validation Big Data
├── performance_metrics.json       # Métriques performance
├── ml_accuracy_chart.png          # Graphique précision ML
├── zone_performance_chart.png     # Graphique zones
├── api_latency_chart.png          # Graphique latence
├── error_distribution.png         # Distribution erreurs
├── system_resources.png           # Ressources système
├── traffic_heatmap.png            # Carte chaleur
└── validation_summary.png         # Résumé validation
```

### Exemple de Rapport JSON

```json
{
  "timestamp": "2024-11-25T22:30:00",
  "summary": {
    "total_tests": 48,
    "passed_tests": 45,
    "success_rate": 93.75,
    "status": "OPERATIONAL"
  },
  "infrastructure": {
    "services_running": 8,
    "services_expected": 8,
    "status": "PASS"
  },
  "ml": {
    "predictions": {
      "status": "PASS",
      "predictions_count": 24,
      "model_info": {
        "type": "ensemble",
        "accuracy": 0.873
      }
    }
  }
}
```

## 🎯 Tests par Catégorie

### Tests d'Infrastructure

```bash
# Vérifier tous les containers
docker ps

# Logs d'un service
docker logs smart-city-postgres

# Statistiques ressources
docker stats
```

### Tests de Base de Données

```bash
# PostgreSQL
docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -c "SELECT COUNT(*) FROM traffic_data;"

# MongoDB
docker exec -it smart-city-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Tests Big Data

```bash
# Logs Spark
docker logs --tail 100 smart-city-spark

# Topics Kafka
docker exec smart-city-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Tests Machine Learning

```bash
# Test via curl
curl "http://localhost:8000/api/v1/predict/traffic/future?zone_id=zone-1&horizon_hours=1"

# Test via script
python tests/test_predictions_ml.py
```

### Tests API

```bash
# Health check
curl http://localhost:8000/health

# Documentation Swagger
# Ouvrir: http://localhost:8000/docs
```

### Tests Dashboards

```bash
# Grafana health
curl http://localhost:3000/api/health

# Ouvrir dashboards
# http://localhost:3000
```

## 📋 Checklist de Validation

Avant de considérer les tests comme complets:

### Prérequis
- [ ] Docker Desktop démarré
- [ ] Services lancés: `docker-compose up -d`
- [ ] Attente 60s pour initialisation
- [ ] Dépendances Python installées

### Exécution Tests
- [ ] Tests infrastructure: `docker ps`
- [ ] Tests PostgreSQL: `validate_database.sql`
- [ ] Tests MongoDB: connexion OK
- [ ] Tests Spark: `validate_bigdata.py`
- [ ] Tests Kafka: topics listés
- [ ] Tests ML: `test_predictions_ml.py`
- [ ] Tests API: tous endpoints OK
- [ ] Tests Grafana: dashboards accessibles

### Validation Résultats
- [ ] Taux de réussite ≥ 80%
- [ ] Tous services actifs
- [ ] Données récentes (< 5 min)
- [ ] Prédictions ML fonctionnelles
- [ ] API latence < 200ms
- [ ] Dashboards affichent données
- [ ] Rapports générés dans `docs/`

### Pour la Soutenance
- [ ] Graphiques générés: `generate_performance_report.py`
- [ ] Rapport final: `VALIDATION_REPORT.md`
- [ ] Métriques JSON: `performance_metrics.json`
- [ ] Captures d'écran dashboards
- [ ] Démonstration API prête

## 🚀 Automatisation

### Script All-in-One (Windows)

```batch
@echo off
echo Demarrage validation complete...

REM 1. Verifier Docker
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo Erreur: Docker non demarre
    exit /b 1
)

REM 2. Demarrer services si necessaire
docker-compose up -d

REM 3. Attendre initialisation
timeout /t 60 /nobreak

REM 4. Executer tous les tests
python tests/comprehensive_validation.py
python tests/validate_bigdata.py
python tests/test_predictions_ml.py
python tests/generate_performance_report.py

REM 5. Afficher rapport
type docs\VALIDATION_REPORT.md

echo.
echo Validation terminee!
pause
```

### CI/CD Integration

```yaml
# .github/workflows/tests.yml
name: Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Wait for services
        run: sleep 60
      - name: Run tests
        run: python tests/comprehensive_validation.py
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: docs/VALIDATION_REPORT.*
```

## 📚 Documentation Complémentaire

- [Guide Complet des Tests](../docs/GUIDE_TESTS_VALIDATION.md)
- [Résultats Détaillés](../docs/RESULTATS_TESTS.md)
- [Résultats pour Soutenance](../docs/SOUTENANCE_RESULTATS.md)
- [Architecture Système](../docs/architecture.md)

## 💡 Conseils

### Avant la Soutenance

1. **Exécuter tous les tests** au moins une fois
2. **Générer tous les graphiques** pour la présentation
3. **Préparer une démonstration** en direct
4. **Avoir un backup** des rapports en PDF
5. **Tester l'accès** aux dashboards Grafana

### Pendant les Tests

1. **Ne pas interrompre** les tests en cours
2. **Attendre la fin** avant de consulter les rapports
3. **Noter les erreurs** pour debugging
4. **Sauvegarder les logs** si problèmes

### Après les Tests

1. **Analyser les résultats** dans les rapports
2. **Corriger les problèmes** si taux < 80%
3. **Regénérer les rapports** après corrections
4. **Archiver les résultats** avec timestamp

---

**Dernière mise à jour:** Novembre 2024  
**Version:** 1.0  
**Mainteneur:** Smart City Platform Team
