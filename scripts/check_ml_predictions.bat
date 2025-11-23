@echo off
echo ================================================
echo Verification Modeles ML et Predictions
echo ================================================
echo.

echo [1] Nombre de predictions en base...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(*) FROM traffic_predictions;"

echo.
echo [2] Types de modeles utilises...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT DISTINCT model_type FROM traffic_predictions;"

echo.
echo [3] Predictions recentes (5 dernieres)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, timestamp, zone_id, prediction_value, actual_value, horizon_min FROM traffic_predictions ORDER BY created_at DESC LIMIT 5;"

echo.
echo [4] Predictions par modele...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, COUNT(*) FROM traffic_predictions GROUP BY model_type;"

echo.
echo [5] Performance modeles (erreur moyenne)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, ROUND(AVG(ABS(prediction_value - COALESCE(actual_value, prediction_value)))::numeric, 2) as mae FROM traffic_predictions WHERE actual_value IS NOT NULL GROUP BY model_type;"

echo.
pause
