@echo off
echo ====================================================================
echo ADAPTATION DASHBOARDS GRAFANA POUR ABIDJAN
echo ====================================================================
echo.
echo Coordonnees GPS : 5.3364°N, -4.0267°W
echo Zones           : zone-centre, zone-nord, zone-est, zone-sud, zone-ouest
echo.

python scripts\adapt_dashboards_abidjan.py

echo.
echo ====================================================================
echo Redemarrage de Grafana...
echo ====================================================================
docker-compose restart grafana

echo.
echo ====================================================================
echo DASHBOARDS ADAPTES POUR ABIDJAN!
echo ====================================================================
echo.
echo Acces Grafana: http://localhost:3000
echo Login: admin / smartcity123
echo.
echo Dashboards mis a jour:
echo   - Smart City Abidjan - Vue d'ensemble
echo   - Smart City Abidjan - Mobilite
echo   - Smart City Abidjan - Trafic
echo   - Smart City Abidjan - Predictions ML
echo   - Et tous les autres...
echo.
echo Centres carte GeoMap: 5.3364°N, -4.0267°W (Abidjan)
echo.
pause
