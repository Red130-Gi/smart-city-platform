@echo off
REM ================================================================
REM Installation des Dépendances Python pour Tests
REM Smart City Platform
REM ================================================================

echo.
echo ================================================================
echo   INSTALLATION DES DEPENDANCES PYTHON
echo ================================================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.8+ depuis: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python est installe
python --version
echo.

REM Vérifier pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] pip n'est pas disponible
    echo.
    echo Reinstaller Python avec l'option "Add to PATH"
    pause
    exit /b 1
)

echo [OK] pip est disponible
pip --version
echo.

REM Mettre à jour pip
echo [1/8] Mise a jour de pip...
python -m pip install --upgrade pip
echo.

REM Installer les dépendances de base
echo [2/8] Installation psycopg2-binary (PostgreSQL)...
pip install psycopg2-binary
echo.

echo [3/8] Installation pymongo (MongoDB)...
pip install pymongo
echo.

echo [4/8] Installation requests (API HTTP)...
pip install requests
echo.

echo [5/8] Installation matplotlib (Graphiques)...
pip install matplotlib
echo.

echo [6/8] Installation seaborn (Visualisations)...
pip install seaborn
echo.

echo [7/8] Installation numpy (Calculs numeriques)...
pip install numpy
echo.

echo [8/8] Installation pandas (Data manipulation)...
pip install pandas
echo.

REM Dépendances optionnelles
echo.
echo Installation des dependances optionnelles...
echo.

echo - kafka-python (Kafka client)...
pip install kafka-python 2>nul
echo.

echo - redis (Redis client)...
pip install redis 2>nul
echo.

echo - jupyter (Notebooks)...
pip install jupyter 2>nul
echo.

REM Vérifier les installations
echo.
echo ================================================================
echo   VERIFICATION DES INSTALLATIONS
echo ================================================================
echo.

python -c "import psycopg2; print('[OK] psycopg2 version:', psycopg2.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] psycopg2 installe avec succes
) else (
    echo [ATTENTION] psycopg2 peut avoir des problemes
)

python -c "import pymongo; print('[OK] pymongo version:', pymongo.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] pymongo installe avec succes
) else (
    echo [ATTENTION] pymongo peut avoir des problemes
)

python -c "import requests; print('[OK] requests version:', requests.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] requests installe avec succes
) else (
    echo [ATTENTION] requests peut avoir des problemes
)

python -c "import matplotlib; print('[OK] matplotlib version:', matplotlib.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] matplotlib installe avec succes
) else (
    echo [ATTENTION] matplotlib peut avoir des problemes
)

python -c "import seaborn; print('[OK] seaborn version:', seaborn.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] seaborn installe avec succes
) else (
    echo [ATTENTION] seaborn peut avoir des problemes
)

python -c "import numpy; print('[OK] numpy version:', numpy.__version__)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] numpy installe avec succes
) else (
    echo [ATTENTION] numpy peut avoir des problemes
)

echo.
echo ================================================================
echo   INSTALLATION TERMINEE
echo ================================================================
echo.

REM Liste toutes les dépendances installées
echo Packages Python installes pour les tests:
echo.
pip list | findstr /I "psycopg2 pymongo requests matplotlib seaborn numpy pandas kafka redis jupyter"
echo.

echo ================================================================
echo   PROCHAINES ETAPES
echo ================================================================
echo.
echo 1. Demarrer Docker Desktop
echo 2. Lancer les services: docker-compose up -d
echo 3. Executer les tests: run_complete_validation.bat
echo 4. Generer les graphiques: python tests/generate_performance_report.py
echo.

REM Proposer de créer un environnement virtuel
echo.
echo RECOMMANDATION: Utiliser un environnement virtuel Python
echo.
echo Pour creer un environnement virtuel:
echo   python -m venv venv
echo   venv\Scripts\activate
echo   pip install -r requirements.txt
echo.

REM Créer un fichier requirements.txt si il n'existe pas
if not exist "requirements.txt" (
    echo Creation de requirements.txt...
    (
        echo # Dependances Python - Smart City Platform
        echo # Installation: pip install -r requirements.txt
        echo.
        echo # Base de donnees
        echo psycopg2-binary==2.9.9
        echo pymongo==4.6.0
        echo redis==5.0.1
        echo.
        echo # API et HTTP
        echo requests==2.31.0
        echo fastapi==0.104.1
        echo uvicorn==0.24.0
        echo.
        echo # Data Science
        echo numpy==1.24.3
        echo pandas==2.0.3
        echo scikit-learn==1.3.2
        echo.
        echo # Visualisation
        echo matplotlib==3.7.3
        echo seaborn==0.13.0
        echo plotly==5.18.0
        echo.
        echo # Big Data
        echo kafka-python==2.0.2
        echo pyspark==3.5.0
        echo.
        echo # Testing
        echo pytest==7.4.3
        echo pytest-asyncio==0.21.1
        echo.
        echo # Utilities
        echo python-dotenv==1.0.0
        echo pydantic==2.5.0
    ) > requirements.txt
    echo [OK] requirements.txt cree
)

echo.
echo Pour installer toutes les dependances en une fois:
echo   pip install -r requirements.txt
echo.
pause
