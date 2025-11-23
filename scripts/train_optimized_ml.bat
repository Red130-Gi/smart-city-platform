@echo off
echo ====================================================================
echo OPTIMIZED ML MODEL TRAINING
echo Target: Reduce MAE from 6.63 km/h to ^< 5 km/h
echo ====================================================================
echo.

echo [1/3] Checking if ML container is running...
docker-compose ps ml-models-runner

echo.
echo [2/3] Copying optimized script to container...
docker cp ml-models\traffic_prediction_optimized.py ml-models-runner:/app/
docker cp ml-models\train_optimized_models.py ml-models-runner:/app/

echo.
echo [3/3] Running optimized training...
docker-compose exec ml-models-runner python train_optimized_models.py

echo.
echo ====================================================================
echo Training completed!
echo Check results above for MAE improvements
echo ====================================================================
echo.
pause
