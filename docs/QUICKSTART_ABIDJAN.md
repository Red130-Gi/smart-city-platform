# 🚀 Quick Start - Abidjan Smart City

## ⚡ DÉMARRAGE EN 3 ÉTAPES

### 1️⃣ Lancer l'Infrastructure (2 minutes)

```bash
# Dans le répertoire du projet
docker-compose up -d
```

**Attendez** que tous les services démarrent (~1-2 minutes).

---

### 2️⃣ Activer Configuration Abidjan (30 secondes)

```bash
.\scripts\activate_abidjan.bat
```

**Ce script fait :**
- ✅ Arrête le générateur générique
- ✅ Copie la configuration Abidjan (10 communes, 5 zones)
- ✅ Active le générateur de données réaliste
- ✅ Démarre la génération

---

### 3️⃣ Vérifier Installation (1 minute)

```bash
.\scripts\verify_abidjan.bat
```

**Vous devriez voir :**
```
zone_id       | nb_capteurs
--------------|-------------
zone-centre   | 6
zone-nord     | 8
zone-est      | 6
zone-sud      | 8
zone-ouest    | 4
```

---

## 🗺️ ACCÈS DASHBOARDS

### Dashboard Principal
```
http://localhost:3000/d/overview-fixed
Login: admin / smartcity123
```

**Vous verrez :**
- 🗺️ Carte d'Abidjan (5.3364°N, -4.0267°W)
- 📊 Vitesse moyenne par zone
- 🚗 Flux de véhicules
- 🔴 Heatmap de congestion

### Dashboard Prédictions ML
```
http://localhost:3000/d/predictions-production
```

**Vous verrez :**
- 🔮 Prédictions 4 modèles (XGBoost, LightGBM, LSTM, Ensemble)
- ⏰ Multi-horizons (5 min, 1h, 6h)
- 🗺️ Prédictions par zone (Centre, Nord, Est, Sud, Ouest)
- ✅ Zones sans congestion

---

## 🎯 CE QUI EST MODÉLISÉ

### 10 Communes Réelles
```
Plateau      → Centre d'affaires (15K hab)
Cocody       → Résidentiel huppé (400K hab)
Yopougon     → Plus grande commune (1,2M hab)
Adjamé       → Commercial/Gare (300K hab)
Treichville  → Port/Historique (130K hab)
Marcory      → Industriel (250K hab)
Koumassi     → Industriel (450K hab)
Port-Bouët   → Aéroport (250K hab)
Attécoubé    → Populaire (300K hab)
Abobo        → Grand Nord (1,2M hab)
```

### 5 Zones de Trafic
```
zone-centre  → Plateau + Adjamé (congestion TRÈS ÉLEVÉE)
zone-nord    → Abobo + Yopougon (congestion ÉLEVÉE)
zone-est     → Cocody + Koumassi (congestion MOYENNE)
zone-sud     → Treichville + Marcory + Port-Bouët (MOYENNE)
zone-ouest   → Yopougon (congestion ÉLEVÉE)
```

### 10 Routes Principales
```
A1 : Boulevard VGE (17 km, 4 voies, 90 km/h)
A2 : Autoroute du Nord (15 km, 4 voies, 100 km/h)
B1 : Boulevard Latrille (3 voies, 70 km/h)
B2 : Boulevard de Marseille (3 voies, 70 km/h)
P1 : Pont Houphouët-Boigny (4 voies, 50 km/h)
P2 : Pont Charles de Gaulle (2 voies, 50 km/h)
P3 : Pont Henri Konan Bédié (6 voies, 90 km/h)
```

### Transport en Commun
```
Bus SOTRA       : 80-120 bus actifs (capacité 100, 150 FCFA)
Gbaka           : Minibus 25 places (200 FCFA)
Woro-woro       : Taxi communal 7 places (300 FCFA)
Taxi compteur   : 4 places (500 FCFA base)
```

---

## ⏰ HEURES DE POINTE

### Matin
```
06:00 - 10:00 (pic à 07:30)
Vitesse moyenne : 12 km/h
Multiplicateur trafic : ×2.5
```

### Midi
```
12:00 - 14:00 (pic à 13:00)
Vitesse moyenne : 18 km/h
Multiplicateur trafic : ×1.4
```

### Soir (PLUS INTENSE)
```
16:30 - 21:00 (pic à 18:30)
Vitesse moyenne : 8 km/h
Multiplicateur trafic : ×3.0
⚠️ Embouteillages critiques sur ponts
```

---

## 🤖 PRÉDICTIONS ML

### Activer Modèles Optimisés

```bash
# Entraîner les modèles (1 fois, 2-5 minutes)
.\scripts\train_optimized_ml.bat

# Activer en production
.\scripts\activate_optimized_ml.bat
```

### Activer Multi-Horizons

```bash
# Activer prédictions court/moyen/long terme
.\scripts\activate_multi_horizon.bat

# Vérifier
.\scripts\check_multi_horizon.bat
```

**Vous aurez :**
- Court terme (+5 min) : MAE 2.34 km/h
- Moyen terme (+1h) : MAE 5-7 km/h
- Long terme (+6h) : MAE 10-12 km/h

---

## 📊 VÉRIFICATIONS

### Données Traffic
```bash
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT zone_id, COUNT(*), ROUND(AVG(speed_kmh), 1) as vitesse FROM traffic_data WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY zone_id;"
```

### Bus SOTRA
```bash
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(DISTINCT vehicle_id) as nb_bus FROM public_transport WHERE timestamp > NOW() - INTERVAL '15 minutes';"
```

**Attendu :** 80-120 bus en journée, 10-30 la nuit

### Parkings
```bash
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT parking_name, capacity, available_spots FROM parking_data WHERE timestamp > NOW() - INTERVAL '15 minutes';"
```

**Attendu :** 8 parkings (Plateau, Adjamé, Cocody, Aéroport, etc.)

---

## 🐛 DÉPANNAGE

### Pas de Données
```bash
# Vérifier services
docker-compose ps

# Relancer générateur
docker-compose restart data-generator

# Voir logs
docker-compose logs -f data-generator
```

### Dashboards Vides
```bash
# Attendre 1-2 minutes pour génération
# Puis actualiser Grafana (F5)

# Vérifier données
.\scripts\check_data.bat
```

### Mauvaises Zones
```bash
# Réactiver Abidjan
.\scripts\activate_abidjan.bat

# Vérifier
.\scripts\verify_abidjan.bat
```

---

## 🎓 POUR DÉMO/SOUTENANCE

### Scénario Typique

**Heure actuelle : 18h00 (Heure de pointe du soir)**

1. **Ouvrir Dashboard Principal**
   ```
   http://localhost:3000/d/overview-fixed
   ```

2. **Montrer Carte Abidjan**
   - Centre : 5.3364°N, -4.0267°W
   - Points rouges : Capteurs de trafic
   - Heatmap : Zones congestionnées

3. **Analyser Congestion**
   ```
   Zone Centre  : 8 km/h  (SATURÉ - Ponts + VGE)
   Zone Nord    : 12 km/h (ÉLEVÉ - Abobo/Yopougon vers centre)
   Zone Ouest   : 10 km/h (ÉLEVÉ - Yopougon congestionné)
   Zone Est     : 25 km/h (MOYEN - Cocody fluide)
   Zone Sud     : 22 km/h (MOYEN - Accès aéroport)
   ```

4. **Ouvrir Dashboard Prédictions**
   ```
   http://localhost:3000/d/predictions-production
   ```

5. **Montrer Prédictions ML**
   - Court terme (+5min) : Congestion stable
   - Moyen terme (+1h) : Amélioration progressive
   - Long terme (+6h) : Retour normal (minuit)

6. **Analyser Impact**
   ```
   "Le système prédit que la congestion persistera jusqu'à 20h30,
   permettant aux conducteurs de planifier ou reporter leurs trajets.
   Économie potentielle : 30-45 Mds FCFA/an pour Abidjan."
   ```

---

## 📚 DOCUMENTATION

| Fichier | Contenu |
|---------|---------|
| `ABIDJAN_SMART_CITY.md` | Configuration géographique complète |
| `ABIDJAN_README.md` | README projet adapté Abidjan |
| `QUICKSTART_ABIDJAN.md` | Ce guide (3 étapes) |
| `MULTI_HORIZON_PREDICTIONS.md` | Prédictions multi-horizons |
| `ML_RESULTS_FINAL.md` | Résultats ML (2.34 km/h) |

---

## ✅ CHECKLIST SUCCÈS

```
☐ docker-compose up -d exécuté
☐ activate_abidjan.bat exécuté
☐ verify_abidjan.bat montre 5 zones
☐ Grafana accessible (http://localhost:3000)
☐ Carte centrée sur Abidjan (5.3364°N, -4.0267°W)
☐ Données en temps réel (rafraîchissement 30s)
☐ Routes avec noms réels (VGE, ponts, etc.)
☐ 80-120 bus SOTRA actifs
☐ 5 zones de congestion colorées
☐ Prédictions ML actives
```

---

## 🚀 COMMANDES RAPIDES

```bash
# Démarrer tout
docker-compose up -d

# Activer Abidjan
.\scripts\activate_abidjan.bat

# Vérifier
.\scripts\verify_abidjan.bat

# ML optimisé
.\scripts\train_optimized_ml.bat
.\scripts\activate_optimized_ml.bat

# Multi-horizons
.\scripts\activate_multi_horizon.bat

# Arrêter
docker-compose down
```

---

**Votre Smart City Platform est maintenant configurée pour Abidjan ! 🇨🇮**

**Temps total : ~5 minutes** ⚡
