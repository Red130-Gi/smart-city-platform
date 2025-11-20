@echo off
echo.
echo ====================================================================
echo   GENERATION DE DONNEES HISTORIQUES BIG DATA (6 MOIS)
echo ====================================================================
echo.
echo Ce script va generer ~3 millions de records sur 6 mois
echo Duree estimee : 2-3 heures
echo.
echo ATTENTION: Cette operation peut prendre plusieurs heures!
echo.
set /p confirm="Voulez-vous continuer? (O/N): "

if /i not "%confirm%"=="O" (
    echo.
    echo Operation annulee.
    exit /b 0
)

echo.
echo ====================================================================
echo COPIE DU SCRIPT DANS LE CONTENEUR...
echo ====================================================================
docker cp data-generation\generate_historical_docker.py data-generator:/app/

echo.
echo ====================================================================
echo GENERATION EN COURS... (Veuillez patienter)
echo ====================================================================
echo.
docker exec data-generator python /app/generate_historical_docker.py

echo.
echo ====================================================================
echo VERIFICATION DU VOLUME
echo ====================================================================
echo.
docker exec postgres psql -U smart_city -d smart_city_db -c "SELECT 'Traffic' AS table, COUNT(*) as records FROM traffic_data UNION ALL SELECT 'Transport', COUNT(*) FROM public_transport UNION ALL SELECT 'Parking', COUNT(*) FROM parking_data"

echo.
echo ====================================================================
echo TERMINÉ!
echo ====================================================================
pause
