@echo off
echo ====================================================================
echo REPARATION GRAFANA
echo ====================================================================
echo.

echo Etape 1: Arret complet...
docker-compose stop grafana
timeout /t 3 /nobreak >nul

echo.
echo Etape 2: Suppression conteneur...
docker-compose rm -f grafana
timeout /t 2 /nobreak >nul

echo.
echo Etape 3: Demarrage propre...
docker-compose up -d grafana

echo.
echo Etape 4: Attente demarrage (30 secondes)...
timeout /t 30 /nobreak

echo.
echo Etape 5: Verification...
docker-compose ps grafana
docker-compose logs --tail 10 grafana

echo.
echo ====================================================================
echo GRAFANA REDEMARRE
echo ====================================================================
echo.
echo Attendez encore 30 secondes puis testez:
echo   http://localhost:3000
echo   Login: admin / smartcity123
echo.
echo Dashboards directs:
echo   http://localhost:3000/d/predictions-production
echo   http://localhost:3000/d/overview-production
echo.
pause
