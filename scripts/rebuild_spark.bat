@echo off
echo ================================================
echo Reconstruction de l'image Spark Streaming
echo ================================================
echo.

echo Arret du service actuel...
docker-compose stop spark-streaming
docker-compose rm -f spark-streaming

echo.
echo Reconstruction de l'image (avec netcat)...
docker-compose build --no-cache spark-streaming

echo.
echo Demarrage du nouveau service...
docker-compose up -d spark-streaming

echo.
echo Attente du demarrage (20 secondes)...
timeout /t 20 /nobreak >nul

echo.
echo ================================================
echo Verification des logs
echo ================================================
docker-compose logs --tail=30 spark-streaming

echo.
echo ================================================
echo Pour voir les logs en temps reel :
echo   docker-compose logs -f spark-streaming
echo ================================================
echo.
pause
