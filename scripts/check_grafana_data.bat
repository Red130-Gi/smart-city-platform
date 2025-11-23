@echo off
echo ================================================
echo Verification des Donnees Grafana
echo ================================================
echo.

echo Execution des requetes SQL...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -f /check_grafana_data.sql

echo.
echo ================================================
echo Verification terminee !
echo ================================================
pause
