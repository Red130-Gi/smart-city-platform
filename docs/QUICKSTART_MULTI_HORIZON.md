# 🚀 Quick Start - Prédictions Multi-Horizons

## ⚡ EN 3 ÉTAPES

### 1️⃣ Activer les Prédictions Multi-Horizons

```bash
.\scripts\activate_multi_horizon.bat
```

**Durée :** ~30 secondes

**Ce qui se passe :**
- ✅ Vérifie les modèles optimisés
- ✅ Active le pipeline multi-horizons
- ✅ Redémarre le conteneur ML

---

### 2️⃣ Vérifier les Prédictions

**Attendre 2-3 minutes** pour que les premières prédictions soient générées.

```bash
.\scripts\check_multi_horizon.bat
```

**Vous devriez voir :**
```
horizon_type | horizon_min | model_type | nb_pred | avg_pred
-------------|-------------|------------|---------|----------
short        | 5           | ensemble   | 2       | 56.2
short        | 5           | xgboost    | 2       | 56.8
short        | 5           | lightgbm   | 2       | 55.9
short        | 5           | lstm       | 2       | 57.1
medium       | 60          | ensemble   | 2       | 52.8
medium       | 60          | xgboost    | 2       | 53.1
...
```

---

### 3️⃣ Visualiser dans Grafana

**URL :** http://localhost:3000/d/predictions-production  
**Login :** admin / smartcity123

**Scrollez en bas** pour voir les 2 nouveaux panels :

1. **⏰ Prédictions Multi-Horizons Ensemble**  
   → Graphique avec 3 courbes (court/moyen/long terme)

2. **📊 Tableau Comparatif Multi-Horizons**  
   → Tableau avec tous modèles × tous horizons

---

## 📊 INTERPRÉTATION

### Graphique Multi-Horizons

```
    60 km/h ┤     ╭──────────  Court terme (+5min)
            │    ╱
    55 km/h ┤   ╱  ╭─────────  Moyen terme (+1h)
            │  ╱  ╱
    50 km/h ┤ ╱  ╱  ╭────────  Long terme (+6h)
            │╱  ╱  ╱
    45 km/h ┼──────────────────────────────────────
             0min      30min        1h         2h
```

**Lecture :**
- Plus la ligne est haute, plus la vitesse prédite est élevée
- Les 3 lignes peuvent diverger (incertitude à long terme)
- La ligne "actuel" (noire) montre la vitesse réelle

---

### Tableau Comparatif

**Exemple :**
```
Horizon         | Ensemble | XGBoost | LightGBM | LSTM  | Actuel
----------------|----------|---------|----------|-------|-------
Court (+5min)   | 56.2     | 56.8    | 55.9     | 57.1  | 55.0
Moyen (+1h)     | 52.8     | 53.1    | 52.4     | 53.5  | 55.0
Long (+6h)      | 48.5     | 49.2    | 47.9     | 49.8  | 55.0
```

**Analyse :**
- **Court terme** : Proche de l'actuel (55 km/h → 56.2 km/h)
- **Moyen terme** : Léger ralentissement prévu (55 → 52.8 km/h)
- **Long terme** : Congestion prévue ce soir (55 → 48.5 km/h)

**Couleurs :**
- 🟢 Vert : > 50 km/h (bon)
- 🟡 Jaune : 40-50 km/h (moyen)
- 🟠 Orange : 30-40 km/h (dense)
- 🔴 Rouge : < 30 km/h (saturé)

---

## 🔄 DÉSACTIVER (Retour Mode Simple)

```bash
docker-compose exec ml-models-runner cp /app/run_pipeline_single.py /app/run_pipeline.py
docker-compose restart ml-models-runner
```

---

## 🎯 CAS D'USAGE

### 1. Navigation Temps Réel
```
Utiliser : Court terme (+5 min)
Précision : ±2-3 km/h
Décision : Éviter carrefour congestionné dans 5 min
```

### 2. Planification Trajets
```
Utiliser : Moyen terme (+1h)
Précision : ±5-7 km/h
Décision : Partir maintenant ou attendre 30 min
```

### 3. Prévisions Journalières
```
Utiliser : Long terme (+6h)
Précision : ±10-12 km/h
Décision : Prévoir heures de pointe du soir
```

---

## 🆘 PROBLÈMES FRÉQUENTS

### ❌ "Pas de données multi-horizons"

**Solution :**
1. Vérifier activation : `.\scripts\check_multi_horizon.bat`
2. Attendre 2-3 minutes
3. Si toujours vide : `.\scripts\activate_multi_horizon.bat`

### ❌ "Panels Grafana vides"

**Solution :**
1. Actualiser la page (F5)
2. Vérifier données : `.\scripts\check_multi_horizon.bat`
3. Attendre 5-10 minutes si vide

### ❌ "Erreur modèles non trouvés"

**Solution :**
```bash
.\scripts\train_optimized_ml.bat
# Attendre fin d'entraînement (2-5 min)
.\scripts\activate_multi_horizon.bat
```

---

## ✅ CHECKLIST SUCCÈS

```
☐ Script activation_multi_horizon.bat exécuté
☐ Logs montrent "Multi-Horizon Predictions"
☐ check_multi_horizon.bat affiche 3 horizons
☐ Grafana affiche graphique multi-horizons
☐ Grafana affiche tableau comparatif
☐ 3 lignes visibles (court/moyen/long)
☐ Couleurs selon vitesse dans tableau
```

---

## 📚 DOCUMENTATION COMPLÈTE

**Fichier :** `docs/MULTI_HORIZON_PREDICTIONS.md`

**Contient :**
- Architecture détaillée
- Algorithmes d'ajustement
- Configuration avancée
- Guide soutenance
- Requêtes SQL
- Dépannage complet

---

**Prédictions multi-horizons opérationnelles en 3 étapes ! 🚀**
