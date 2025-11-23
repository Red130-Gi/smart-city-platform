@echo off
echo ====================================================================
echo VERIFICATION PREDICTIONS MODELES OPTIMISES
echo ====================================================================
echo.

echo [1] Predictions recentes par modele...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, COUNT(*), ROUND(AVG(prediction_value)::numeric, 2) as avg_pred FROM traffic_predictions WHERE timestamp > NOW() - INTERVAL '10 minutes' GROUP BY model_type ORDER BY model_type;"

echo.
echo [2] Dernieres predictions (toutes)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, timestamp, ROUND(prediction_value::numeric, 2) as pred, ROUND(actual_value::numeric, 2) as actual FROM traffic_predictions ORDER BY created_at DESC LIMIT 5;"

echo.
echo [3] Verification presence Ensemble et LightGBM...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT model_type, COUNT(*) FROM traffic_predictions WHERE model_type IN ('ensemble', 'lightgbm') GROUP BY model_type;"

echo.
pause
