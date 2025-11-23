@echo off
echo ====================================================================
echo VERIFICATION PREDICTIONS MULTI-HORIZONS
echo ====================================================================
echo.

echo [1/3] Verification table predictions...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT COUNT(*) as total_predictions, COUNT(DISTINCT horizon_type) as nb_horizons FROM traffic_predictions WHERE timestamp > NOW() - INTERVAL '1 hour';"

echo.
echo [2/3] Predictions par horizon (derniere heure)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT horizon_type, horizon_min, model_type, COUNT(*) as nb_pred, ROUND(AVG(prediction_value)::numeric, 1) as avg_pred FROM traffic_predictions WHERE timestamp > NOW() - INTERVAL '1 hour' GROUP BY horizon_type, horizon_min, model_type ORDER BY horizon_min, model_type;"

echo.
echo [3/3] Dernieres predictions (par horizon)...
docker-compose exec -T postgres psql -U smart_city -d smart_city_db -c "SELECT DISTINCT ON (horizon_type, model_type) horizon_type, model_type, ROUND(prediction_value::numeric, 1) as pred, ROUND(actual_value::numeric, 1) as actual, TO_CHAR(timestamp, 'HH24:MI') as time FROM traffic_predictions WHERE timestamp > NOW() - INTERVAL '30 minutes' ORDER BY horizon_type, model_type, created_at DESC;"

echo.
echo ====================================================================
echo INTERPRETATION:
echo ====================================================================
echo - short  : Court terme  (+5 min)   - Precision maximale
echo - medium : Moyen terme  (+1 heure) - Planification trajets
echo - long   : Long terme   (+6 heures)- Previsions journalieres
echo.
echo Si aucun horizon n'est affiche, executez:
echo    .\scripts\activate_multi_horizon.bat
echo.
pause
