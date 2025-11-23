# 🗺️ Dashboard ML - Ajout Prédictions par Zone

**Date :** 20 Novembre 2024  
**Status :** ✅ **PANELS AJOUTÉS**

---

## 🎯 NOUVEAUX PANELS AJOUTÉS

### 1. 🗺️ Prédictions par Zone (5 Zones)

**Position :** En bas à gauche du dashboard

**Description :** Affiche les prédictions des modèles ML pour chacune des 5 zones de la ville, avec comparaison entre Ensemble, LightGBM et vitesse actuelle.

**Colonnes :**
- **zone** : Nom de la zone (zone-1, zone-2, zone-3, zone-4, zone-5)
- **ensemble_kmh** : Prédiction du modèle Ensemble (production)
- **lightgbm_kmh** : Prédiction du modèle LightGBM (champion)
- **actuel_kmh** : Vitesse actuelle mesurée
- **etat** : État de congestion prévu
  - ✅ **Fluide** : > 50 km/h
  - 🟡 **Moyen** : 35-50 km/h
  - 🟠 **Dense** : 25-35 km/h
  - 🔴 **Saturé** : < 25 km/h

**Requête SQL :**
```sql
WITH zones AS (
  SELECT UNNEST(ARRAY['zone-1', 'zone-2', 'zone-3', 'zone-4', 'zone-5']) as zone_name
),
latest_pred AS (
  SELECT 
    td.zone_id,
    AVG(CASE WHEN tp.model_type = 'ensemble' THEN tp.prediction_value END) as pred_ensemble,
    AVG(CASE WHEN tp.model_type = 'lightgbm' THEN tp.prediction_value END) as pred_lightgbm,
    AVG(td.speed_kmh) as speed_actual
  FROM traffic_data td
  LEFT JOIN traffic_predictions tp ON tp.timestamp > NOW() - INTERVAL '15 minutes'
  WHERE td.timestamp > NOW() - INTERVAL '15 minutes'
    AND td.zone_id IS NOT NULL
  GROUP BY td.zone_id
)
SELECT 
  COALESCE(lp.zone_id, z.zone_name) as zone,
  ROUND(COALESCE(lp.pred_ensemble, 50.0)::numeric, 1) as ensemble_kmh,
  ROUND(COALESCE(lp.pred_lightgbm, 50.0)::numeric, 1) as lightgbm_kmh,
  ROUND(COALESCE(lp.speed_actual, 50.0)::numeric, 1) as actuel_kmh,
  CASE 
    WHEN COALESCE(lp.pred_ensemble, 50) > 50 THEN 'Fluide'
    WHEN COALESCE(lp.pred_ensemble, 50) > 35 THEN 'Moyen'
    WHEN COALESCE(lp.pred_ensemble, 50) > 25 THEN 'Dense'
    ELSE 'Sature'
  END as etat
FROM zones z
LEFT JOIN latest_pred lp ON z.zone_name = lp.zone_id
ORDER BY z.zone_name
```

**Couleurs :**
- Vert : Vitesse > 50 km/h (bon)
- Jaune : 40-50 km/h (moyen)
- Orange : 30-40 km/h (dense)
- Rouge : < 30 km/h (saturé)

**Exemple de Données :**
```
Zone    | Ensemble | LightGBM | Actuel | État
--------|----------|----------|--------|-------
zone-1  | 58.3     | 60.1     | 55.2   | Fluide
zone-2  | 42.5     | 44.8     | 40.1   | Moyen
zone-3  | 31.2     | 33.5     | 30.5   | Dense
zone-4  | 65.7     | 68.2     | 62.3   | Fluide
zone-5  | 22.8     | 25.1     | 20.5   | Sature
```

---

### 2. ✅ Zones SANS Congestion Prévue

**Position :** En bas à droite du dashboard

**Description :** Filtre et affiche UNIQUEMENT les zones où la circulation sera fluide (vitesse prédite ≥ 45 km/h). Permet d'identifier rapidement les meilleures routes.

**Colonnes :**
- **zone** : Nom de la zone
- **vitesse_predite_kmh** : Prédiction Ensemble
- **vitesse_actuelle_kmh** : Vitesse actuelle
- **statut** : "Circulation Fluide" (toujours)

**Requête SQL :**
```sql
WITH zones AS (
  SELECT UNNEST(ARRAY['zone-1', 'zone-2', 'zone-3', 'zone-4', 'zone-5']) as zone_name
),
latest_pred AS (
  SELECT 
    td.zone_id,
    AVG(CASE WHEN tp.model_type = 'ensemble' THEN tp.prediction_value END) as pred_ensemble,
    AVG(td.speed_kmh) as speed_actual
  FROM traffic_data td
  LEFT JOIN traffic_predictions tp ON tp.timestamp > NOW() - INTERVAL '15 minutes'
  WHERE td.timestamp > NOW() - INTERVAL '15 minutes'
    AND td.zone_id IS NOT NULL
  GROUP BY td.zone_id
)
SELECT 
  COALESCE(lp.zone_id, z.zone_name) as zone,
  ROUND(COALESCE(lp.pred_ensemble, 50.0)::numeric, 1) as vitesse_predite_kmh,
  ROUND(COALESCE(lp.speed_actual, 50.0)::numeric, 1) as vitesse_actuelle_kmh,
  'Circulation Fluide' as statut
FROM zones z
LEFT JOIN latest_pred lp ON z.zone_name = lp.zone_id
WHERE COALESCE(lp.pred_ensemble, 50) >= 45
ORDER BY COALESCE(lp.pred_ensemble, 50) DESC
```

**Seuil :** Vitesse prédite ≥ 45 km/h

**Tri :** Par vitesse prédite décroissante (zones les plus fluides en premier)

**Couleur :** Fond vert clair pour toutes les lignes (circulation fluide)

**Exemple de Données :**
```
Zone    | Vitesse Prédite | Vitesse Actuelle | Statut
--------|-----------------|------------------|-------------------
zone-4  | 65.7            | 62.3             | Circulation Fluide
zone-1  | 58.3            | 55.2             | Circulation Fluide
zone-2  | 48.5            | 45.1             | Circulation Fluide
```

**Note :** Si toutes les zones sont congestionnées (< 45 km/h), la table sera vide.

---

## 🎯 CAS D'USAGE

### Pour les Conducteurs
**Utiliser "Zones SANS Congestion" pour :**
- Choisir le meilleur itinéraire en temps réel
- Éviter les zones congestionnées
- Planifier un trajet optimal

### Pour les Gestionnaires de Trafic
**Utiliser "Prédictions par Zone" pour :**
- Surveiller toutes les zones simultanément
- Anticiper les congestions futures
- Réagir avant qu'un problème ne survienne

---

## 🔍 LOGIQUE DES 5 ZONES

Les zones sont définies comme :
- **zone-1** : Centre-ville
- **zone-2** : Périphérie Nord
- **zone-3** : Périphérie Est
- **zone-4** : Périphérie Sud
- **zone-5** : Périphérie Ouest

**Notes :**
- Si une zone n'a pas de données récentes, valeur par défaut = 50 km/h
- Les prédictions utilisent le modèle Ensemble (production)
- Mise à jour toutes les 30 secondes

---

## 📊 INTERPRÉTATION DES ÉTATS

### Fluide (Vert)
- Vitesse prédite : > 50 km/h
- Temps de trajet : Normal
- Action : Aucune

### Moyen (Jaune)
- Vitesse prédite : 35-50 km/h
- Temps de trajet : +10-30%
- Action : Surveiller

### Dense (Orange)
- Vitesse prédite : 25-35 km/h
- Temps de trajet : +30-60%
- Action : Envisager itinéraire alternatif

### Saturé (Rouge)
- Vitesse prédite : < 25 km/h
- Temps de trajet : +60-100%
- Action : ⚠️ Éviter cette zone !

---

## 🎓 POUR LA SOUTENANCE

### Démonstration Panel "Prédictions par Zone"

**Message :**
> "Ce panel affiche les prédictions ML pour chacune des 5 zones de la ville. On voit ici que zone-4 sera fluide avec 65.7 km/h prédit, tandis que zone-5 sera saturée avec 22.8 km/h. Le modèle Ensemble et LightGBM sont tous deux affichés pour comparaison, et l'état de congestion est calculé automatiquement selon des seuils de vitesse."

**Points à montrer :**
1. Les 5 zones affichées systématiquement
2. Comparaison Ensemble vs LightGBM vs Actuel
3. Colonne "État" avec couleur selon congestion
4. Mise à jour temps réel (30s)

---

### Démonstration Panel "Zones SANS Congestion"

**Message :**
> "Ce panel filtre intelligemment les zones où la circulation sera fluide (≥ 45 km/h). Il permet aux conducteurs et aux systèmes de navigation d'identifier instantanément les meilleures routes disponibles. Ici, on voit que 3 zones sur 5 seront fluides dans les prochaines minutes, avec zone-4 en tête à 65.7 km/h."

**Points à montrer :**
1. Filtrage automatique (seulement zones fluides)
2. Tri par vitesse décroissante
3. Fond vert pour visibilité immédiate
4. Footer indiquant le nombre de zones fluides

---

### Scénario d'Utilisation Réel

**Situation :**
```
Heure de pointe (18h)
zone-1 : 25 km/h (Saturé)  ❌
zone-2 : 38 km/h (Moyen)   🟡
zone-3 : 32 km/h (Dense)   🟠
zone-4 : 62 km/h (Fluide)  ✅
zone-5 : 55 km/h (Fluide)  ✅
```

**Panel "Zones SANS Congestion" affichera :**
```
zone-4 : 62 km/h
zone-5 : 55 km/h
```

**Décision Smart :**
- 🚗 Conducteur : Prendre zone-4 ou zone-5
- 🚦 Système : Suggérer itinéraire via zone-4 (plus rapide)
- 📊 Gestionnaire : Réguler feux de zone-1 pour désengorger

---

## 🐛 DÉPANNAGE

### Panel vide "Prédictions par Zone"

**Cause :** Pas de données dans traffic_data avec zone_id

**Solution :**
```sql
-- Vérifier données zones
SELECT DISTINCT zone_id FROM traffic_data 
WHERE timestamp > NOW() - INTERVAL '15 minutes' 
  AND zone_id IS NOT NULL;
```

**Si vide :** Les données sont générées sans zone_id, les valeurs par défaut (50 km/h) s'afficheront

---

### Panel vide "Zones SANS Congestion"

**Cause :** Toutes les zones sont congestionnées (< 45 km/h)

**Solution :** C'est normal ! Cela signifie qu'il n'y a pas de zone fluide actuellement.

**Message à afficher :** "Aucune zone fluide pour le moment - Toutes les zones sont congestionnées"

---

### Valeurs à 50 km/h partout

**Cause :** Pas de prédictions récentes ou pas de données traffic_data

**Solution :**
1. Vérifier pipeline ML actif
2. Vérifier générateur de données actif
3. Attendre 1 minute pour nouvelles prédictions

---

## 📊 REQUÊTES UTILES

### Vérifier Zones Disponibles
```sql
SELECT zone_id, COUNT(*), AVG(speed_kmh)::numeric(5,1) as avg_speed
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY zone_id
ORDER BY zone_id;
```

### Vérifier Prédictions par Zone
```sql
SELECT 
  COALESCE(zone_id, 'global') as zone,
  model_type,
  COUNT(*) as nb_pred,
  AVG(prediction_value)::numeric(5,1) as avg_pred
FROM traffic_predictions
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY zone_id, model_type
ORDER BY zone_id, model_type;
```

### Compter Zones Fluides
```sql
SELECT COUNT(*) as nb_zones_fluides
FROM traffic_data td
WHERE td.timestamp > NOW() - INTERVAL '15 minutes'
  AND td.zone_id IS NOT NULL
  AND td.speed_kmh >= 45
GROUP BY td.zone_id;
```

---

## ✅ RÉSUMÉ

**Panels Ajoutés :** 2

### 1. 🗺️ Prédictions par Zone
```
✅ Affiche 5 zones systématiquement
✅ Prédictions Ensemble + LightGBM
✅ Vitesse actuelle comparative
✅ État de congestion calculé
✅ Couleurs selon seuils
```

### 2. ✅ Zones SANS Congestion
```
✅ Filtre zones fluides (≥ 45 km/h)
✅ Tri par vitesse décroissante
✅ Fond vert pour visibilité
✅ Aide à la décision routière
```

---

## 🚀 ACCÈS

```
http://localhost:3000/d/predictions-production
Login: admin / smartcity123
```

**Position des panels :** En bas du dashboard (ligne y=24)

**Rafraîchissement :** Automatique toutes les 30 secondes

---

**Dashboard ML maintenant complet avec prédictions par zone et zones fluides ! 🗺️✅**
