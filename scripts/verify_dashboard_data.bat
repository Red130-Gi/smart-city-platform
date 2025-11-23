@echo off
echo ================================================
echo Verification des Donnees Dashboard Grafana
echo ================================================
echo.

echo Attente de 10 secondes pour que Grafana redémarre...
timeout /t 10 /nobreak >nul

echo.
echo ================================================
echo SCHÉMA PostgreSQL
echo ================================================
echo.
echo Tables disponibles:
echo   - public_transport (colonne: vehicle_id)
echo   - taxis (PAS taxi_data)
echo   - traffic_data
echo   - parking_data
echo.

echo ================================================
echo VÉRIFICATION DES DONNÉES
echo ================================================
echo.

echo [1/4] Bus actifs (dernières 5 min)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(DISTINCT vehicle_id) FROM public_transport WHERE timestamp > NOW() - INTERVAL '5 minutes';"

echo.
echo [2/4] Taxis disponibles (dernières 5 min)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(*) FROM taxis WHERE status = 'available' AND timestamp > NOW() - INTERVAL '5 minutes';"

echo.
echo [3/4] Trajets taxi aujourd'hui...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(*) FROM taxis WHERE DATE(timestamp) = CURRENT_DATE AND status = 'occupied';"

echo.
echo [4/4] Voitures par zone...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT zone_id, AVG(vehicle_flow)::integer as flux_moyen FROM traffic_data WHERE timestamp > NOW() - INTERVAL '5 minutes' GROUP BY zone_id ORDER BY zone_id;"

echo.
echo ================================================
echo VOLUMES TOTAUX
echo ================================================
echo.
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT 'Traffic' as table_name, COUNT(*) FROM traffic_data UNION ALL SELECT 'Bus', COUNT(*) FROM public_transport UNION ALL SELECT 'Taxis', COUNT(*) FROM taxis;"

echo.
echo ================================================
echo Dashboard accessible sur:
echo   http://localhost:3000/d/real-data-prod
echo   Login: admin / smartcity123
echo ================================================
echo.
pause
