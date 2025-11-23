@echo off
echo ================================================
echo Stopping Spark Streaming Service
echo ================================================
echo.

docker-compose stop spark-streaming
docker-compose rm -f spark-streaming

echo.
echo Spark Streaming stopped successfully.
echo.
pause
