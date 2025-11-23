@echo off
echo ====================================================================
echo ACTIVATION PREDICTIONS MULTI-HORIZONS
echo ====================================================================
echo.
echo Court terme  : +5 min   (Precision maximale)
echo Moyen terme  : +1 heure (Planification trajets)
echo Long terme   : +6 heures (Previsions journalieres)
echo.

echo [1/4] Configuration base de donnees...
call scripts\setup_multi_horizon_db.bat

echo.
echo [2/4] Verification des modeles optimises...
docker-compose exec ml-models-runner ls -lh /app/xgboost_optimized.pkl /app/lightgbm_optimized.pkl /app/lstm_optimized.h5 /app/scalers_optimized.pkl 2>nul
if errorlevel 1 (
    echo.
    echo ÔØî ERREUR: Modeles optimises non trouves!
    echo Executez d'abord: .\scripts\train_optimized_ml.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Ô£à Modeles optimises trouves!
echo.

echo [3/4] Copie du pipeline multi-horizons...
docker cp ml-models\run_pipeline_multi_horizon.py ml-models-runner:/app/

echo.
echo [4/4] Sauvegarde et activation...
docker-compose exec ml-models-runner cp /app/run_pipeline.py /app/run_pipeline_single.py
docker-compose exec ml-models-runner cp /app/run_pipeline_multi_horizon.py /app/run_pipeline.py

echo.
echo Redemarrage du conteneur ML...
docker-compose restart ml-models-runner

echo.
echo ====================================================================
echo Ô£à PIPELINE MULTI-HORIZONS ACTIVE!
echo ====================================================================
echo.
echo Predictions generees:
echo   - Court terme  : +5 min   (MAE ~2.3 km/h)
echo   - Moyen terme  : +1 heure (MAE ~5-7 km/h)
echo   - Long terme   : +6 heures (MAE ~10-12 km/h)
echo.
echo Verifiez dans Grafana: http://localhost:3000/d/predictions-production
echo.
echo Pour revenir au mode simple:
echo    docker-compose exec ml-models-runner cp /app/run_pipeline_single.py /app/run_pipeline.py
echo    docker-compose restart ml-models-runner
echo.
pause
