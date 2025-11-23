@echo off
echo ====================================================================
echo VERIFICATION CONFIGURATION ABIDJAN
echo ====================================================================
echo.

echo [1/5] Verification des zones de trafic...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT DISTINCT zone_id, COUNT(*) as nb_capteurs FROM traffic_data WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY zone_id ORDER BY zone_id;"

echo.
echo Zones attendues : zone-centre, zone-nord, zone-est, zone-sud, zone-ouest
echo.

echo [2/5] Verification des communes...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT road_name, zone_id, ROUND(AVG(speed_kmh)::numeric, 1) as vitesse_moyenne FROM traffic_data WHERE timestamp > NOW() - INTERVAL '30 minutes' GROUP BY road_name, zone_id ORDER BY zone_id LIMIT 10;"

echo.
echo [3/5] Verification transport en commun (Bus SOTRA)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(DISTINCT vehicle_id) as nb_bus_actifs, ROUND(AVG(speed_kmh)::numeric, 1) as vitesse_moyenne, ROUND(AVG(occupancy_percent)::numeric, 1) as occupation_moyenne FROM public_transport WHERE timestamp > NOW() - INTERVAL '15 minutes';"

echo.
echo [4/5] Verification parkings...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT parking_name, zone_id, capacity, occupied_spots, available_spots FROM parking_data WHERE timestamp > NOW() - INTERVAL '15 minutes' ORDER BY zone_id LIMIT 8;"

echo.
echo [5/5] Statistiques generales...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT 'Capteurs trafic' as type, COUNT(*) as total FROM traffic_data WHERE timestamp > NOW() - INTERVAL '1 hour' UNION ALL SELECT 'Bus SOTRA', COUNT(*) FROM public_transport WHERE timestamp > NOW() - INTERVAL '1 hour' UNION ALL SELECT 'Parkings', COUNT(*) FROM parking_data WHERE timestamp > NOW() - INTERVAL '1 hour';"

echo.
echo ====================================================================
echo INTERPRETATION
echo ====================================================================
echo.
echo Si vous voyez:
echo   - 5 zones de trafic (centre, nord, est, sud, ouest) ........... OK
echo   - Routes avec noms realistes (VGE, Latrille, ponts, etc.) .... OK
echo   - 80-120 bus SOTRA actifs en journee .......................... OK
echo   - 8 parkings avec capacites 200-600 ........................... OK
echo.
echo Configuration Abidjan est active!
echo.
echo Acces Grafana: http://localhost:3000
echo Login: admin / smartcity123
echo.
pause
