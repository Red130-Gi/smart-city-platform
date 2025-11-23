@echo off
echo ====================================================================
echo CONFIGURATION BASE DE DONNEES MULTI-HORIZONS
echo ====================================================================
echo.
echo Ajout des colonnes horizon_min et horizon_type...
echo.

docker cp add_horizon_columns.sql postgres:/tmp/add_horizon_columns.sql
docker-compose exec postgres psql -U smart_city -d smart_city_db -f /tmp/add_horizon_columns.sql

echo.
echo ====================================================================
echo Colonnes ajoutees avec succes!
echo ====================================================================
echo.
echo Verification de la structure de la table:
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "\d traffic_predictions"

echo.
echo Grafana sera redemarre dans 3 secondes...
timeout /t 3 /nobreak >nul
docker-compose restart grafana

echo.
echo ====================================================================
echo CONFIGURATION TERMINEE!
echo ====================================================================
echo.
echo Les panels multi-horizons devraient maintenant fonctionner.
echo Actualisez Grafana: http://localhost:3000/d/predictions-production
echo.
pause
