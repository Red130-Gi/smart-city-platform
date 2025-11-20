-- Tests pour vérifier que les données sont disponibles dans PostgreSQL
-- Exécuter avec : docker-compose exec postgres psql -U smart_city -d smart_city_db -f /tests/test_grafana_data.sql

-- Test 1: Vérifier les tables
\dt

-- Test 2: Compter les enregistrements récents de trafic
SELECT 'Traffic Data Count' AS test, COUNT(*) AS count 
FROM traffic_data 
WHERE timestamp > NOW() - INTERVAL '10 minutes';

-- Test 3: Vitesse moyenne actuelle
SELECT 'Average Speed' AS metric, ROUND(AVG(speed_kmh)::numeric, 1) AS value
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '5 minutes';

-- Test 4: Transport public actif
SELECT 'Active Public Transport' AS metric, COUNT(DISTINCT vehicle_id) AS count
FROM public_transport
WHERE timestamp > NOW() - INTERVAL '5 minutes'
  AND status = 'active';

-- Test 5: Occupation des parkings
SELECT 'Parking Occupancy' AS metric, ROUND(AVG(occupancy_rate)::numeric, 1) AS percentage
FROM parking_data
WHERE timestamp > NOW() - INTERVAL '5 minutes';

-- Test 6: Distribution par zone
SELECT zone_id, 
       COUNT(*) as sensor_count,
       ROUND(AVG(speed_kmh)::numeric, 1) as avg_speed
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '10 minutes'
GROUP BY zone_id
ORDER BY zone_id;

-- Test 7: État des lignes de bus
SELECT line_number,
       COUNT(DISTINCT vehicle_id) as vehicles,
       ROUND(AVG(passenger_count)::numeric, 0) as avg_passengers,
       ROUND(AVG(delay_minutes)::numeric, 1) as avg_delay
FROM public_transport
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY line_number
ORDER BY line_number
LIMIT 10;

-- Test 8: Données les plus récentes
SELECT 'Latest Traffic Data' AS info, MAX(timestamp) AS last_update 
FROM traffic_data;

SELECT 'Latest Transport Data' AS info, MAX(timestamp) AS last_update 
FROM public_transport;

SELECT 'Latest Parking Data' AS info, MAX(timestamp) AS last_update 
FROM parking_data;
