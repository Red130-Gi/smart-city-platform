@echo off
echo ================================================
echo Spark Streaming Live Logs
echo ================================================
echo Press Ctrl+C to exit
echo ================================================
echo.

docker-compose logs -f spark-streaming
