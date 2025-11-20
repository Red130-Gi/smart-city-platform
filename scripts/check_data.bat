@echo off
echo.
echo ====================================
echo Checking Database Data for Grafana
echo ====================================
echo.

echo Traffic Data Count:
docker exec postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(*) FROM traffic_data"

echo.
echo Public Transport Count:
docker exec postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(*) FROM public_transport"

echo.
echo Parking Data Count:
docker exec postgres psql -U smart_city -d smart_city_db -t -c "SELECT COUNT(*) FROM parking_data"

echo.
echo ====================================
echo Done!
echo ====================================
