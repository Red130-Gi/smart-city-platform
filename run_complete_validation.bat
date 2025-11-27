@echo off
REM ================================================================
REM VALIDATION COMPLÈTE - SMART CITY PLATFORM
REM Tests: Infrastructure, Base de données, Big Data, ML, Dashboards
REM ================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================
echo     VALIDATION COMPLETE - SMART CITY PLATFORM
echo ================================================================
echo     Date: %date% %time%
echo ================================================================
echo.

REM Couleurs pour le terminal (si supporté)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

REM Vérifier que Docker est en cours d'exécution
echo [ETAPE 1/6] Verification de Docker Desktop...
echo ----------------------------------------------------------------
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERREUR]%RESET% Docker Desktop n'est pas demarre
    echo.
    echo Actions requises:
    echo   1. Demarrer Docker Desktop
    echo   2. Attendre que Docker soit completement charge
    echo   3. Relancer ce script
    echo.
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Docker Desktop est actif
echo.

REM Vérifier les services Docker
echo [ETAPE 2/6] Verification des services...
echo ----------------------------------------------------------------
docker-compose ps
echo.

REM Si les services ne sont pas démarrés, les démarrer
echo Voulez-vous demarrer les services si necessaire? (O/N)
set /p START_SERVICES="> "
if /i "%START_SERVICES%"=="O" (
    echo Demarrage des services...
    docker-compose up -d
    echo.
    echo Attente du demarrage complet (30 secondes)...
    timeout /t 30 /nobreak >nul
    echo.
)

REM Test de la base de données PostgreSQL
echo [ETAPE 3/6] Validation de la base de donnees PostgreSQL...
echo ----------------------------------------------------------------
if exist "tests\validate_database.sql" (
    echo Execution des tests SQL...
    docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -f /tests/validate_database.sql 2>nul
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Tests SQL executes avec succes
    ) else (
        echo %YELLOW%[INFO]%RESET% Execution directe des tests...
        docker exec smart-city-postgres psql -U smartcity -d smartcitydb -c "SELECT COUNT(*) as traffic_records FROM traffic_data;"
        docker exec smart-city-postgres psql -U smartcity -d smartcitydb -c "SELECT COUNT(*) as predictions FROM predictions;"
        docker exec smart-city-postgres psql -U smartcity -d smartcitydb -c "SELECT COUNT(*) as zones FROM zones;"
    )
) else (
    echo %YELLOW%[INFO]%RESET% Script SQL de validation non trouve
    echo Verification basique...
    docker exec smart-city-postgres psql -U smartcity -d smartcitydb -c "\dt"
)
echo.

REM Test Big Data et Spark
echo [ETAPE 4/6] Validation Big Data (Spark/Kafka)...
echo ----------------------------------------------------------------
if exist "tests\validate_bigdata.py" (
    echo Execution des tests Big Data...
    python tests\validate_bigdata.py
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Tests Big Data executes
    ) else (
        echo %YELLOW%[ATTENTION]%RESET% Certains tests Big Data ont echoue
    )
) else (
    echo %YELLOW%[INFO]%RESET% Script Python de validation Big Data non trouve
    echo Verification manuelle...
    docker logs --tail 50 smart-city-spark
)
echo.

REM Test des modèles ML
echo [ETAPE 5/6] Validation des modeles Machine Learning...
echo ----------------------------------------------------------------
if exist "tests\test_predictions_ml.py" (
    echo Execution des tests ML...
    python tests\test_predictions_ml.py
    if %errorlevel% equ 0 (
        echo %GREEN%[OK]%RESET% Tests ML executes avec succes
    ) else (
        echo %YELLOW%[ATTENTION]%RESET% L'API ML n'est peut-etre pas accessible
    )
) else (
    echo %YELLOW%[INFO]%RESET% Script de test ML non trouve
)
echo.

REM Validation complète avec script Python
echo [ETAPE 6/6] Validation complete et generation du rapport...
echo ----------------------------------------------------------------
if exist "tests\comprehensive_validation.py" (
    echo Execution de la validation complete...
    python tests\comprehensive_validation.py
    if %errorlevel% equ 0 (
        echo.
        echo %GREEN%[OK]%RESET% Validation complete terminee avec succes
        echo.
        echo Rapports generes:
        echo   - docs\VALIDATION_REPORT.json
        echo   - docs\VALIDATION_REPORT.md
        echo   - docs\BIGDATA_VALIDATION_REPORT.json
    ) else (
        echo %YELLOW%[ATTENTION]%RESET% Validation complete avec avertissements
    )
) else (
    echo %YELLOW%[INFO]%RESET% Script de validation complete non trouve
    echo Installation des dependances...
    pip install psycopg2-binary pymongo requests 2>nul
)
echo.

REM Afficher un résumé
echo ================================================================
echo     RESUME DE LA VALIDATION
echo ================================================================
echo.

REM Compter les services actifs
for /f %%i in ('docker ps --format "{{.Names}}" ^| find /c /v ""') do set SERVICE_COUNT=%%i
echo Services Docker actifs: %SERVICE_COUNT%

REM Vérifier PostgreSQL
docker exec smart-city-postgres psql -U smartcity -d smartcitydb -c "SELECT COUNT(*) FROM traffic_data LIMIT 1" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% PostgreSQL - Operationnel
) else (
    echo %RED%[KO]%RESET% PostgreSQL - Probleme detecte
)

REM Vérifier MongoDB
docker exec smart-city-mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% MongoDB - Operationnel
) else (
    echo %RED%[KO]%RESET% MongoDB - Probleme detecte
)

REM Vérifier Grafana
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% Grafana - Accessible sur http://localhost:3000
) else (
    echo %RED%[KO]%RESET% Grafana - Non accessible
)

REM Vérifier l'API
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo %GREEN%[OK]%RESET% API - Accessible sur http://localhost:8000
) else (
    echo %RED%[KO]%RESET% API - Non accessible
)

echo.
echo ================================================================
echo     VALIDATION TERMINEE
echo ================================================================
echo.
echo Prochaines etapes:
echo   1. Consulter les rapports dans le dossier 'docs/'
echo   2. Verifier les dashboards Grafana: http://localhost:3000
echo   3. Tester l'API: http://localhost:8000/docs
echo   4. Consulter les logs si des erreurs sont detectees
echo.

REM Proposer d'ouvrir les rapports
echo Voulez-vous ouvrir les rapports de validation? (O/N)
set /p OPEN_REPORTS="> "
if /i "%OPEN_REPORTS%"=="O" (
    if exist "docs\VALIDATION_REPORT.md" (
        start docs\VALIDATION_REPORT.md
    )
    if exist "docs\BIGDATA_VALIDATION_REPORT.json" (
        start docs\BIGDATA_VALIDATION_REPORT.json
    )
)

echo.
pause
