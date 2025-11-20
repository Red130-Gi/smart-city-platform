@echo off
REM Script de publication sur GitHub - Smart City Platform
REM Auteur: Votre Nom
REM Date: 20 novembre 2024

echo ╔════════════════════════════════════════════════════════════╗
echo ║  Smart City Platform - Publication GitHub                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Vérifier si Git est installé
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git n'est pas installé !
    echo Téléchargez-le depuis : https://git-scm.com/download/win
    pause
    exit /b 1
)

echo ✅ Git est installé
echo.

REM Se placer dans le dossier du projet
cd /d "%~dp0\.."

REM Vérifier si .gitignore existe
if not exist ".gitignore" (
    echo ⚠️  .gitignore n'existe pas. Création...
    echo __pycache__/ > .gitignore
    echo *.pyc >> .gitignore
    echo .env >> .gitignore
    echo data/*.csv >> .gitignore
    echo *.log >> .gitignore
    echo ✅ .gitignore créé
    echo.
)

REM Vérifier si déjà initialisé
if exist ".git" (
    echo ⚠️  Git est déjà initialisé dans ce dossier
    echo.
    goto :add_files
)

REM Initialiser Git
echo 📦 Initialisation du repository Git...
git init
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'initialisation
    pause
    exit /b 1
)
echo ✅ Repository Git initialisé
echo.

REM Configurer Git (si pas déjà fait)
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Configuration de Git:
    set /p username="Entrez votre nom: "
    set /p email="Entrez votre email: "
    git config --global user.name "%username%"
    git config --global user.email "%email%"
    echo ✅ Configuration Git terminée
    echo.
)

:add_files
REM Ajouter les fichiers
echo 📁 Ajout des fichiers au staging...
git add .
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de l'ajout des fichiers
    pause
    exit /b 1
)
echo ✅ Fichiers ajoutés
echo.

REM Afficher le statut
echo 📊 Statut du repository:
git status --short
echo.

REM Demander confirmation
set /p confirm="Voulez-vous créer le commit initial ? (o/n): "
if /i not "%confirm%"=="o" (
    echo ❌ Opération annulée
    pause
    exit /b 0
)

REM Créer le commit
echo.
echo 💾 Création du commit initial...
git commit -m "Initial commit: Smart City Platform - Big Data & IA"
if %errorlevel% neq 0 (
    echo ❌ Erreur lors du commit
    pause
    exit /b 1
)
echo ✅ Commit créé avec succès
echo.

REM Vérifier si remote existe déjà
git remote -v | findstr "origin" >nul 2>&1
if %errorlevel% equ 0 (
    echo ℹ️  Remote 'origin' existe déjà
    git remote -v
    echo.
    set /p update_remote="Voulez-vous mettre à jour l'URL du remote ? (o/n): "
    if /i "%update_remote%"=="o" (
        set /p repo_url="Entrez l'URL du repository GitHub (https://github.com/USERNAME/smart-city-platform.git): "
        git remote set-url origin !repo_url!
        echo ✅ Remote mis à jour
    )
) else (
    echo.
    echo 🌐 Configuration du remote GitHub
    echo.
    echo Allez sur https://github.com et créez un nouveau repository:
    echo   - Nom: smart-city-platform
    echo   - Description: Plateforme intelligente de mobilité basée sur Big Data et IA
    echo   - Public ou Private (votre choix)
    echo   - NE PAS initialiser avec README (vous en avez déjà un)
    echo.
    set /p repo_url="Entrez l'URL du repository GitHub (ex: https://github.com/USERNAME/smart-city-platform.git): "
    
    git remote add origin %repo_url%
    if %errorlevel% neq 0 (
        echo ❌ Erreur lors de l'ajout du remote
        pause
        exit /b 1
    )
    echo ✅ Remote ajouté: %repo_url%
)
echo.

REM Renommer la branche en 'main'
git branch -M main
echo ✅ Branche renommée en 'main'
echo.

REM Pousser vers GitHub
echo 🚀 Push vers GitHub...
echo.
echo ⚠️  Vous allez être invité à vous authentifier:
echo    - Username: votre nom d'utilisateur GitHub
echo    - Password: votre Personal Access Token (PAS votre mot de passe)
echo.
echo Pour créer un token:
echo    1. GitHub → Settings → Developer settings → Personal access tokens
echo    2. Generate new token (classic)
echo    3. Cochez 'repo' (full control)
echo    4. Copiez le token généré (ghp_...)
echo.
pause

git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo ❌ Erreur lors du push
    echo.
    echo Si l'authentification a échoué, essayez:
    echo   1. Créer un Personal Access Token sur GitHub
    echo   2. Installer GitHub CLI: winget install GitHub.cli
    echo   3. Exécuter: gh auth login
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  ✅ SUCCÈS ! Projet publié sur GitHub                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Votre projet est maintenant disponible sur:
git remote get-url origin
echo.
echo 📋 Prochaines étapes:
echo   1. Vérifiez votre repository sur GitHub
echo   2. Ajoutez une description et des topics (Big Data, AI, Smart City)
echo   3. Activez GitHub Pages pour la documentation (optionnel)
echo   4. Invitez des collaborateurs (optionnel)
echo.
pause
