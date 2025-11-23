@echo off
echo ====================================================================
echo DIAGNOSTIC GRAFANA
echo ====================================================================
echo.

echo [1/5] Etat du conteneur...
docker-compose ps grafana

echo.
echo [2/5] Verification dashboards dans le conteneur...
docker exec grafana ls -lh /etc/grafana/provisioning/dashboards/json/

echo.
echo [3/5] Derniers logs (20 lignes)...
docker-compose logs --tail 20 grafana

echo.
echo [4/5] Test connexion HTTP...
curl -s -o nul -w "Status HTTP: %%{http_code}\n" http://localhost:3000/api/health

echo.
echo [5/5] Verification PostgreSQL datasource...
docker exec grafana ls -lh /etc/grafana/provisioning/datasources/

echo.
echo ====================================================================
echo ACCES GRAFANA
echo ====================================================================
echo.
echo URL   : http://localhost:3000
echo Login : admin
echo Pass  : smartcity123
echo.
echo Si erreur "Failed to load home dashboard":
echo   - Les dashboards sont dans /etc/grafana/provisioning/dashboards/json/
echo   - Grafana charge automatiquement tous les .json
echo   - Aller directement a: http://localhost:3000/dashboards
echo.
echo Dashboards disponibles:
echo   http://localhost:3000/d/predictions-production
echo   http://localhost:3000/d/overview-production
echo   http://localhost:3000/d/traffic-production
echo.
pause
