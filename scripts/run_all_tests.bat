@echo off
REM ===============================================
REM Script de tests complets - Smart City Platform
REM ===============================================

echo.
echo ========================================
echo TESTS ET VALIDATION - SMART CITY
echo ========================================
echo.

REM Verifier que Docker est en cours d'execution
echo [1/8] Verification de Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Docker Desktop n'est pas demarre
    echo Veuillez demarrer Docker Desktop et relancer ce script
    pause
    exit /b 1
)
echo [OK] Docker est actif
echo.

REM Verifier l'etat des services
echo [2/8] Verification des services Docker...
docker-compose ps
echo.

REM Test de la base de donnees PostgreSQL
echo [3/8] Test de la base de donnees...
docker exec -it smart-city-postgres psql -U smartcity -d smartcitydb -c "\dt" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PostgreSQL est accessible
) else (
    echo [ATTENTION] PostgreSQL n'est pas accessible
)
echo.

REM Test de MongoDB
echo [4/8] Test de MongoDB...
docker exec -it smart-city-mongodb mongosh --eval "db.adminCommand('ping')" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MongoDB est accessible
) else (
    echo [ATTENTION] MongoDB n'est pas accessible
)
echo.

REM Test de Kafka
echo [5/8] Test de Kafka...
docker exec -it smart-city-kafka kafka-topics --list --bootstrap-server localhost:9092 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Kafka est accessible
) else (
    echo [ATTENTION] Kafka n'est pas accessible
)
echo.

REM Test de Grafana
echo [6/8] Test de Grafana...
curl -s http://localhost:3000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Grafana est accessible sur http://localhost:3000
) else (
    echo [ATTENTION] Grafana n'est pas accessible
)
echo.

REM Test de l'API
echo [7/8] Test de l'API...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] API est accessible sur http://localhost:8000
) else (
    echo [ATTENTION] API n'est pas accessible
)
echo.

REM Executer les tests Python ML
echo [8/8] Execution des tests ML Python...
if exist "tests\test_predictions_ml.py" (
    python tests\test_predictions_ml.py
) else (
    echo [ATTENTION] Fichier de test Python non trouve
)
echo.

echo ========================================
echo TESTS TERMINES
echo ========================================
echo.
echo Consultez le rapport de validation genere dans docs/
pause
