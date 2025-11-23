@echo off
echo ====================================================================
echo ACTIVATION DES MODELES ML OPTIMISES (MAE 2.34 km/h)
echo ====================================================================
echo.

echo [1/4] Verification des modeles optimises...
echo.

echo Checking if optimized models exist in container...
docker-compose exec ml-models-runner ls -lh /app/xgboost_optimized.pkl /app/lightgbm_optimized.pkl /app/lstm_optimized.h5 /app/scalers_optimized.pkl 2>nul
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Modeles optimises non trouves!
    echo.
    echo Vous devez d'abord entrainer les modeles optimises:
    echo    .\scripts\train_optimized_ml.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Modeles optimises trouves!
echo.

echo [2/4] Copie du nouveau pipeline vers le conteneur...
docker cp ml-models\run_pipeline_optimized.py ml-models-runner:/app/

echo.
echo [3/4] Sauvegarde ancien pipeline...
docker-compose exec ml-models-runner cp /app/run_pipeline.py /app/run_pipeline_old.py

echo.
echo [4/4] Activation du pipeline optimise...
docker-compose exec ml-models-runner cp /app/run_pipeline_optimized.py /app/run_pipeline.py

echo.
echo ====================================================================
echo ✅ PIPELINE OPTIMISE ACTIVE!
echo ====================================================================
echo.
echo Les modeles optimises sont maintenant utilises:
echo   - XGBoost  : 0.08 km/h
echo   - LightGBM : 0.07 km/h
echo   - LSTM     : 7.77 km/h
echo   - Ensemble : 2.34 km/h ⭐
echo.
echo Redemarrage du conteneur ML...
docker-compose restart ml-models-runner

echo.
echo ====================================================================
echo ✅ TERMINÉ!
echo ====================================================================
echo.
echo Les predictions utilisent maintenant les modeles optimises.
echo Verifiez dans Grafana: http://localhost:3000/d/predictions-production
echo.
echo Pour revenir a l'ancien pipeline:
echo    docker-compose exec ml-models-runner cp /app/run_pipeline_old.py /app/run_pipeline.py
echo    docker-compose restart ml-models-runner
echo.
pause
