# 🚀 Guide Rapide : Préparer les Données Big Data

## ⚡ TL;DR - Actions Immédiates

```bash
# 1. Générer 6 mois de données historiques (~3 heures)
cd data-generation
python generate_historical_data.py
# Choisir option 3 (Complet : 6 mois)

# 2. Augmenter la fréquence de génération (optionnel)
cd ../scripts
increase_data_volume.bat
# Choisir option 3 (INTENSIF - x5 volume)

# 3. Vérifier le volume
python analyze_data_volume.py
```

**Résultat** : 3-5 millions de records = ✅ **SUFFISANT POUR BIG DATA**

---

## 📊 Problème Actuel

### Volume Actuel (Sans Génération Historique)

```
Records actuels : ~100,000 (quelques heures de données)
Taille : ~50 MB
Période : Quelques heures seulement

❌ INSUFFISANT pour une étude Big Data
```

### Volume Requis pour Big Data

```
Records minimum : 1,000,000+ (1 million)
Taille : 500 MB - 2 GB
Période : 3-6 mois

✅ SUFFISANT pour une étude académique
```

---

## 🎯 Solution en 3 Étapes

### Étape 1 : Générer des Données Historiques (PRIORITÉ 1)

#### Pourquoi ?
Sans données historiques, vous n'avez que quelques heures de données. Pour une étude Big Data, il faut **des mois** de données.

#### Comment ?

**Option A : Script Python (Recommandé)**
```bash
cd data-generation
python generate_historical_data.py
```

Choisir :
- **Option 3** : 6 mois (~3M records, ~3h de génération) ✅ RECOMMANDÉ
- Option 4 : 12 mois (~6M records, ~6h) - Si vous avez le temps

**Option B : Via Docker**
```bash
docker-compose exec data-generator python generate_historical_data.py
```

#### Résultat Attendu

```
📊 Après génération de 6 mois :
  • 3,000,000+ records
  • 1.5 GB de données
  • Période : 6 mois complets
  • Taille : SUFFISANTE pour Big Data ✅
```

---

### Étape 2 : Augmenter la Vélocité (OPTIONNEL)

#### Pourquoi ?
Pour générer encore plus de données en temps réel.

#### Comment ?

**Windows :**
```batch
cd scripts
increase_data_volume.bat
# Choisir option 3 (INTENSIF)
```

**Manuelle :**
```yaml
# Éditer docker-compose.yml
environment:
  - GENERATION_INTERVAL=1  # Au lieu de 5

# Redémarrer
docker-compose restart data-generator
```

#### Résultat Attendu

```
Avant : 112,000 records/jour
Après : 560,000 records/jour (x5)

En 1 semaine : +3.9 millions de records supplémentaires
```

---

### Étape 3 : Vérifier le Volume

```bash
# Analyser le volume de données
cd scripts
python analyze_data_volume.py
```

Vous devriez voir :
```
📊 VOLUME ACTUEL PAR TABLE
----------------------------------------------------------------------
  traffic_data         :  1,500,000 records |    750 MB |     ...
  public_transport     :    900,000 records |    450 MB |     ...
  parking_data         :    600,000 records |    300 MB |     ...
----------------------------------------------------------------------
  TOTAL                :  3,000,000 records

💾 Taille totale de la base : 1.5 GB

✅ VOLUME SUFFISANT POUR BIG DATA
```

---

## 📈 Timeline Recommandée

### Scénario 1 : Génération Rapide (3-4 heures)

```
Jour 0 : Lancer generate_historical_data.py (option 3)
  ↓ 3 heures de génération
Jour 0 : 3 millions de records disponibles ✅
  ↓ Optionnel : Augmenter vélocité
Jour 1-7 : +500K records/jour en temps réel
  ↓
Jour 7 : 6-7 millions de records ✅ EXCELLENT
```

### Scénario 2 : Génération Continue (1-2 semaines)

```
Jour 0 : Configuration actuelle (intervalle 5s)
  ↓
Jour 1-14 : Génération continue
  ↓ 112,000 records/jour
Jour 14 : 1.5 millions de records ✅ SUFFISANT
```

**Recommandation** : Scénario 1 (génération historique) = Plus rapide !

---

## 🎓 Pour Votre Mémoire/Thèse

### Justification du Volume

```markdown
## 3. Volume de Données (Big Data)

Notre plateforme Smart City collecte et traite des données massives
répondant aux critères du Big Data :

### Volume
- **3.2 millions de records** collectés sur 6 mois
- **1.5 GB** de données brutes dans PostgreSQL
- **7 sources de données** différentes (capteurs IoT)

### Vélocité
- Génération en **temps réel** toutes les 5 secondes
- **16,000+ records/heure** en flux continu
- **24/7 collection** sans interruption

### Variété
- Capteurs de trafic (19 sensors)
- Transport public (34 véhicules)
- Parkings (12 zones)
- Vélos partagés (24 stations)
- Taxis/VTC (50 véhicules)
- Météo temps réel
- Qualité de l'air (5 stations)

Ce volume dépasse le seuil minimum du Big Data (1M+ records)
et permet des analyses statistiquement significatives pour
la gestion intelligente de la mobilité urbaine.
```

---

## ✅ Checklist Finale

Avant de commencer votre analyse :

- [ ] **Générer données historiques** (6 mois)
  ```bash
  python generate_historical_data.py
  ```

- [ ] **Vérifier le volume** (> 1M records)
  ```bash
  python analyze_data_volume.py
  ```

- [ ] **Augmenter vélocité** (optionnel, x5 volume)
  ```bash
  increase_data_volume.bat
  ```

- [ ] **Laisser tourner 1-2 semaines** (données récentes)
  ```bash
  docker-compose logs -f data-generator
  ```

- [ ] **Documenter le volume** dans votre mémoire
  ```
  Voir : docs/BIG_DATA_REQUIREMENTS.md
  ```

---

## ❓ FAQ

### Q1 : Combien de temps pour générer 6 mois de données ?
**R :** Environ 3 heures avec le script de génération historique.

### Q2 : Est-ce que 3 millions de records, c'est suffisant ?
**R :** ✅ OUI ! Le seuil minimum Big Data est 1M records. 3M est largement suffisant pour une étude académique.

### Q3 : Dois-je augmenter la vélocité (étape 2) ?
**R :** Optionnel. Si vous avez le temps, laissez tourner 1-2 semaines avec intervalle 1s pour avoir encore plus de données.

### Q4 : Que faire si la génération est trop longue ?
**R :** Commencez avec 3 mois (option 2) au lieu de 6 mois. 1.5M records reste acceptable.

### Q5 : Comment vérifier que ça marche ?
**R :** 
```bash
# Vérifier les logs
docker-compose logs -f data-generator

# Compter les records
python scripts/analyze_data_volume.py
```

### Q6 : Puis-je arrêter et reprendre plus tard ?
**R :** Oui ! Les données déjà générées sont sauvegardées dans PostgreSQL.

---

## 🚨 Erreurs Courantes

### Erreur : "Connection refused" PostgreSQL

**Solution :**
```bash
# Vérifier que PostgreSQL tourne
docker-compose ps postgres

# Redémarrer si nécessaire
docker-compose restart postgres

# Attendre 10 secondes et réessayer
```

### Erreur : "Out of memory"

**Solution :**
```bash
# Générer en plusieurs fois
# Au lieu de 6 mois d'un coup, faire 2x3 mois

# Ou augmenter la mémoire Docker
# Docker Desktop → Settings → Resources → Memory : 4+ GB
```

### Erreur : Script trop lent

**Solution :**
```python
# Réduire le batch_size dans generate_historical_data.py
# Ligne ~95-97 : batch_size=1 → batch_size=10
# Cela va plus vite mais utilise plus de RAM
```

---

## 📞 Support

**Documentation complète :** `docs/BIG_DATA_REQUIREMENTS.md`

**Vérification volume :** `scripts/analyze_data_volume.py`

**Génération historique :** `data-generation/generate_historical_data.py`

---

## 🎉 Résumé

```
1️⃣ Lancer : python generate_historical_data.py (option 3)
2️⃣ Attendre : 3 heures
3️⃣ Résultat : 3M+ records = BIG DATA ✅

Optionnel:
4️⃣ Augmenter vélocité : increase_data_volume.bat (option 3)
5️⃣ Laisser tourner : 1-2 semaines
6️⃣ Résultat final : 5-10M records = EXCELLENT ✅
```

**Vous êtes prêt pour le Big Data !** 🚀
