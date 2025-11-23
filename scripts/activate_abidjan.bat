@echo off
echo ====================================================================
echo ACTIVATION CONFIGURATION ABIDJAN
echo ====================================================================
echo.
echo Ville cible : Abidjan, Cote d'Ivoire
echo Population  : ~5 millions d'habitants
echo Communes    : 10 (Plateau, Cocody, Yopougon, Adjame, etc.)
echo Zones       : 5 zones de trafic strategiques
echo.

echo [1/4] Arret du generateur actuel...
docker-compose stop data-generator

echo.
echo [2/4] Copie du generateur Abidjan...
docker cp data-generation\abidjan_data_generator.py data-generator:/app/data_generators_abidjan.py
docker cp config\abidjan_config.py data-generator:/app/abidjan_config.py

echo.
echo [3/4] Configuration environnement...
docker-compose exec data-generator sh -c "cd /app && python -c \"import abidjan_config; print('Config Abidjan chargee:', len(abidjan_config.COMMUNES), 'communes')\" "

echo.
echo [4/4] Demarrage generateur Abidjan...
docker-compose up -d data-generator

echo.
echo ====================================================================
echo ABIDJAN SMART CITY ACTIVE!
echo ====================================================================
echo.
echo Configuration:
echo   - 10 communes (Plateau, Cocody, Yopougon, Adjame, Treichville...)
echo   - 5 zones de trafic (Centre, Nord, Est, Sud, Ouest)
echo   - 10 routes principales (VGE, Autoroute du Nord, Ponts...)
echo   - Transport: Bus SOTRA, Gbaka, Woro-woro, Taxis
echo.
echo Coordonnees GPS: 5.3364°N, -4.0267°W
echo.
echo Prochaines etapes:
echo   1. Verifier les donnees: .\scripts\check_data.bat
echo   2. Voir dashboards Grafana: http://localhost:3000
echo   3. Dashboard predictions: http://localhost:3000/d/predictions-production
echo.
echo Pour utiliser le nouveau generateur manuellement:
echo   docker-compose exec data-generator python /app/data_generators_abidjan.py
echo.
pause
