@echo off
echo =========================================
echo    Smart City Platform - Demarrage
echo =========================================

REM Verifier Docker
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Docker n'est pas installe ou n'est pas en cours d'execution.
    echo Veuillez installer Docker Desktop et le demarrer.
    pause
    exit /b 1
)

echo OK Docker detecte

REM Creer les repertoires necessaires
echo Creation des repertoires...
if not exist "grafana\provisioning\dashboards\json" mkdir "grafana\provisioning\dashboards\json"
if not exist "data\kafka" mkdir "data\kafka"
if not exist "data\mongodb" mkdir "data\mongodb"
if not exist "data\postgres" mkdir "data\postgres"

REM Demarrer les services de base
echo Demarrage des services de base...
docker-compose up -d zookeeper kafka mongodb postgres redis minio

REM Attendre que les services soient prets
echo Attente de l'initialisation des services (30s)...
timeout /t 30 /nobreak >nul

REM Demarrer Spark
echo Demarrage de Spark...
docker-compose up -d spark-master spark-worker

REM Attendre Spark
timeout /t 10 /nobreak >nul

REM Demarrer Grafana
echo Demarrage de Grafana...
docker-compose up -d grafana

REM Demarrer l'API
echo Demarrage de l'API...
docker-compose up -d api

REM Attendre l'API
timeout /t 10 /nobreak >nul

REM Demarrer le generateur de donnees
echo Demarrage du generateur de donnees...
docker-compose up -d data-generator

echo.
echo =========================================
echo    Smart City Platform demarree !
echo =========================================
echo.
echo URLs d'acces:
echo    - Grafana:        http://localhost:3000
echo      User: admin / Pass: smartcity123
echo    - API:            http://localhost:8000
echo    - API Docs:       http://localhost:8000/docs
echo    - Spark UI:       http://localhost:8080
echo    - MinIO Console:  http://localhost:9001
echo.
echo Logs:
echo    docker-compose logs -f [service]
echo.
echo Pour arreter:
echo    scripts\stop.bat
echo =========================================
pause
