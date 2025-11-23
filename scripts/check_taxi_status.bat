@echo off
echo ================================================
echo Diagnostic Taxis
echo ================================================
echo.

echo [1] Nombre total de taxis dans la base...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(*) FROM taxis;"

echo.
echo [2] Taxis des 5 dernières minutes...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(*) FROM taxis WHERE timestamp > NOW() - INTERVAL '5 minutes';"

echo.
echo [3] Valeurs UNIQUES du champ 'status'...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT DISTINCT status FROM taxis;"

echo.
echo [4] Répartition par status (dernières 5 min)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT status, COUNT(*) FROM taxis WHERE timestamp > NOW() - INTERVAL '5 minutes' GROUP BY status;"

echo.
echo [5] Échantillon de données taxis...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT taxi_id, status, timestamp FROM taxis ORDER BY timestamp DESC LIMIT 10;"

echo.
pause
