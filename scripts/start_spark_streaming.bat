@echo off
echo ================================================
echo Starting Spark Streaming Service
echo ================================================
echo.

echo Checking Docker services...
docker-compose ps

echo.
echo Building Spark Streaming image...
docker-compose build spark-streaming

echo.
echo Starting Spark Streaming job...
docker-compose up -d spark-streaming

echo.
echo Waiting for Spark to start (30 seconds)...
timeout /t 30 /nobreak >nul

echo.
echo ================================================
echo Spark Streaming Status
echo ================================================
docker-compose ps spark-streaming

echo.
echo ================================================
echo Recent Logs (last 50 lines)
echo ================================================
docker-compose logs --tail=50 spark-streaming

echo.
echo ================================================
echo To view live logs, run:
echo   docker-compose logs -f spark-streaming
echo ================================================
echo.
pause
