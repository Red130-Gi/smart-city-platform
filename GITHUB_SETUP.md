# 🚀 Guide de Publication sur GitHub

## Étape 1 : Préparation du Projet

### A. Créer un fichier .gitignore

```bash
# Créer .gitignore à la racine du projet
```

Contenu recommandé :

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb

# Machine Learning Models (optionnel - peut être volumineux)
ml-models/mlruns/
*.h5
*.pkl
*.joblib
models/*.pth

# Données (ne pas commit les données massives)
data/*.csv
data/*.json
data/historical/
*.db

# Docker
*.log

# Environnement
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Grafana
grafana/data/

# PostgreSQL
postgres-data/

# Logs
logs/
*.log

# Temporaires
tmp/
temp/
*.tmp
```

### B. Vérifier la structure du projet

Assurez-vous que votre projet a cette structure :

```
smart-city-platform/
├── api/                    # API FastAPI
├── data-generation/        # Générateurs de données
├── data-pipeline/          # Scripts Spark
├── ml-models/             # Modèles ML
├── dashboard/             # Interface React (optionnel)
├── grafana/               # Dashboards Grafana
├── docs/                  # Documentation
│   └── memoire/          # Mémoire universitaire
├── scripts/               # Scripts utilitaires
├── docker-compose.yml
├── README.md
├── .gitignore            # À créer
└── LICENSE               # À créer
```

---

## Étape 2 : Initialisation Git

### A. Installer Git (si nécessaire)

**Windows :**
```bash
# Télécharger depuis https://git-scm.com/download/win
# Ou avec Chocolatey :
choco install git
```

**Vérifier l'installation :**
```bash
git --version
# Doit afficher : git version 2.x.x
```

### B. Configuration Git

```bash
# Configurer nom et email
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Vérifier la configuration
git config --list
```

### C. Initialiser le repository

```bash
# Se placer dans le dossier du projet
cd c:\memoire\smart-city-platform

# Initialiser Git
git init

# Vérifier le statut
git status
```

---

## Étape 3 : Premier Commit

### A. Ajouter les fichiers

```bash
# Ajouter tous les fichiers (respecte .gitignore)
git add .

# Vérifier ce qui sera commité
git status

# Si vous voulez exclure certains fichiers :
# git reset <fichier>
```

### B. Créer le commit initial

```bash
git commit -m "Initial commit: Smart City Platform - Big Data & IA"
```

---

## Étape 4 : Créer le Repository GitHub

### A. Via l'interface web GitHub

1. **Aller sur GitHub** : https://github.com
2. **Se connecter** ou créer un compte
3. **Cliquer sur "+"** (en haut à droite) → **"New repository"**

### B. Paramètres du repository

```yaml
Repository name: smart-city-platform
Description: Plateforme intelligente de services urbains de mobilité 
             basée sur Big Data et IA - Projet de mémoire

Visibilité:
  - Public : ✅ Recommandé (partage, portfolio)
  - Private : Si vous voulez garder privé

Initialize:
  - README : ❌ NON (vous en avez déjà un)
  - .gitignore : ❌ NON (déjà créé)
  - License : ✅ OUI - Choisir "MIT License"
```

4. **Cliquer sur "Create repository"**

---

## Étape 5 : Connecter Local à GitHub

### A. Ajouter le remote

GitHub vous donnera des commandes, utilisez la version HTTPS :

```bash
# Ajouter l'origine remote
git remote add origin https://github.com/VOTRE_USERNAME/smart-city-platform.git

# Vérifier
git remote -v
```

### B. Pousser le code

```bash
# Renommer la branche en 'main' (si nécessaire)
git branch -M main

# Pousser vers GitHub
git push -u origin main
```

**Note :** Lors du premier push, GitHub vous demandera de vous authentifier.

---

## Étape 6 : Authentification GitHub

### Option 1 : Personal Access Token (Recommandé)

1. **Aller dans GitHub** → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token** (classic)
3. **Nom** : "Smart City Platform"
4. **Scopes** : Cocher `repo` (full control)
5. **Generate token**
6. **COPIER LE TOKEN** (vous ne le reverrez plus !)

```bash
# Au moment du push, utilisez :
Username: votre_username
Password: ghp_votre_token_généré
```

### Option 2 : GitHub CLI (Plus simple)

```bash
# Installer GitHub CLI
winget install GitHub.cli

# S'authentifier
gh auth login

# Suivre les instructions interactives
# Choisir : HTTPS, Login with a web browser
```

---

## Étape 7 : Améliorer le README

### A. Créer un README.md attractif

```bash
# Le README existant est déjà bon, mais vous pouvez l'améliorer
```

Éléments à ajouter :

```markdown
# 🏙️ Smart City Platform - Big Data & IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-24.0+-blue.svg)](https://www.docker.com/)

> Plateforme intelligente de services urbains de mobilité et transport urbain 
> basée sur le Big Data et l'Intelligence Artificielle.

## 🎯 Projet de Mémoire

**Université :** [Votre Université]  
**Année :** 2024-2025  
**Domaine :** Big Data & Intelligence Artificielle

## 📊 Résultats

✅ **3,42 millions** de records générés (6 mois)  
✅ **87,3%** de précision ML (Ensemble Learning)  
✅ **89ms** de latence API (objectif < 200ms)  
✅ **99,9%** de disponibilité SLA

## 🚀 Démarrage Rapide

```bash
# Cloner le projet
git clone https://github.com/VOTRE_USERNAME/smart-city-platform.git
cd smart-city-platform

# Lancer la plateforme
docker-compose up -d

# Accéder aux services
Grafana: http://localhost:3000 (admin/smartcity123)
API: http://localhost:8000/docs
```

## 📚 Documentation

- [Architecture](docs/architecture.md)
- [Validation Big Data](docs/BIGDATA_VALIDATION_REPORT.md)
- [Mémoire Complet](docs/memoire/)
- [Guide de Démarrage](QUICKSTART.md)

## 🛠️ Technologies

- **Streaming:** Apache Kafka 7.5
- **Processing:** Apache Spark 3.5
- **Storage:** PostgreSQL 15, MongoDB 6, Redis 7
- **ML:** XGBoost, TensorFlow, Scikit-learn
- **Visualization:** Grafana 10
- **Orchestration:** Docker Compose

## 📝 Citation

Si vous utilisez ce projet dans vos recherches :

```bibtex
@mastersthesis{smartcity2024,
  author = {Votre Nom},
  title = {Conception d'une Plateforme Intelligente de Services Urbains 
           de Mobilité basée sur Big Data et IA},
  school = {Votre Université},
  year = {2024}
}
```

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour plus de détails.
```

---

## Étape 8 : Ajouter une License

```bash
# GitHub a déjà créé LICENSE si vous l'avez choisi lors de la création
# Sinon, créez LICENSE à la racine :
```

**Contenu MIT License :**

```
MIT License

Copyright (c) 2024 Votre Nom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Étape 9 : Workflow Git pour Futures Modifications

### A. Faire des modifications

```bash
# 1. Modifier des fichiers
# ... éditer vos fichiers ...

# 2. Voir les changements
git status
git diff

# 3. Ajouter les changements
git add <fichier>
# ou tout ajouter :
git add .

# 4. Commiter
git commit -m "feat: ajout nouvelle fonctionnalité"

# 5. Pousser vers GitHub
git push origin main
```

### B. Conventions de commit

```bash
# Types de commit recommandés :
git commit -m "feat: ajout prédiction long terme"
git commit -m "fix: correction bug cache Redis"
git commit -m "docs: mise à jour README"
git commit -m "refactor: optimisation pipeline Spark"
git commit -m "test: ajout tests unitaires ML"
git commit -m "perf: amélioration latence API"
```

---

## Étape 10 : GitHub Pages (Optionnel)

### Publier la documentation

```bash
# 1. Créer branche gh-pages
git checkout -b gh-pages

# 2. Pousser vers GitHub
git push origin gh-pages

# 3. Aller dans Settings → Pages
# Source: Branch gh-pages
# Votre doc sera sur : https://VOTRE_USERNAME.github.io/smart-city-platform/
```

---

## Étape 11 : Badges et Statistiques

### Ajouter des badges au README

```markdown
![GitHub stars](https://img.shields.io/github/stars/VOTRE_USERNAME/smart-city-platform)
![GitHub forks](https://img.shields.io/github/forks/VOTRE_USERNAME/smart-city-platform)
![GitHub issues](https://img.shields.io/github/issues/VOTRE_USERNAME/smart-city-platform)
![GitHub last commit](https://img.shields.io/github/last-commit/VOTRE_USERNAME/smart-city-platform)
```

---

## 📋 Checklist Complète

- [ ] Créer `.gitignore`
- [ ] Initialiser Git (`git init`)
- [ ] Premier commit (`git commit -m "Initial commit"`)
- [ ] Créer repository sur GitHub
- [ ] Ajouter remote (`git remote add origin ...`)
- [ ] Pousser le code (`git push -u origin main`)
- [ ] Configurer authentification (Token ou GitHub CLI)
- [ ] Améliorer README avec badges
- [ ] Ajouter LICENSE (MIT recommandé)
- [ ] Vérifier que tout est bien poussé
- [ ] Tester le clone depuis GitHub

---

## 🔒 Sécurité : Fichiers Sensibles

**IMPORTANT : Ne JAMAIS commiter :**

```bash
# Vérifiez que ces fichiers sont dans .gitignore
.env
*.env
database.ini
secrets.yaml
credentials.json
*.key
*.pem
```

**Si vous avez déjà commité des secrets par erreur :**

```bash
# Supprimer de l'historique Git
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret/file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (attention : destructif)
git push origin --force --all
```

---

## 🌟 Bonnes Pratiques

1. **Commits réguliers** : Commiter souvent avec messages clairs
2. **Branches** : Utiliser des branches pour nouvelles features
3. **Pull Requests** : Même seul, pour garder un historique propre
4. **Documentation** : Maintenir README à jour
5. **Issues** : Utiliser GitHub Issues pour tracker bugs/features
6. **Releases** : Taguer les versions importantes (`git tag v1.0.0`)

---

## 📞 Aide et Ressources

**Documentation Git :**
- https://git-scm.com/doc
- https://docs.github.com/

**Commandes utiles :**
```bash
git status          # Voir l'état des fichiers
git log            # Historique des commits
git diff           # Voir les changements
git branch         # Lister les branches
git checkout -b    # Créer nouvelle branche
git pull           # Récupérer changements
git clone          # Cloner un repository
```

**En cas de problème :**
```bash
# Annuler dernier commit (garde les changements)
git reset --soft HEAD~1

# Annuler tous les changements non commités
git reset --hard

# Voir le remote
git remote -v
```

---

**Votre projet sera bientôt visible sur GitHub ! 🎉**

*Guide créé le 20 novembre 2024*
