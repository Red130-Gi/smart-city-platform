-- Vérification des données pour Grafana

-- 1. Nombre de bus actifs
SELECT COUNT(DISTINCT bus_id) as bus_actifs
FROM public_transport
WHERE timestamp > NOW() - INTERVAL '5 minutes';

-- 2. Nombre de taxis disponibles
SELECT COUNT(*) as taxis_disponibles
FROM taxi_data
WHERE status = 'available'
AND timestamp > NOW() - INTERVAL '5 minutes';

-- 3. Trajets aujourd'hui
SELECT COUNT(*) as trajets_jour
FROM taxi_data
WHERE DATE(timestamp) = CURRENT_DATE
AND status = 'occupied';

-- 4. Voitures par zone (traffic)
SELECT zone_id, COUNT(*) as nb_capteurs, AVG(vehicle_flow) as flux_moyen
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '5 minutes'
GROUP BY zone_id
ORDER BY zone_id;

-- 5. Total records dans chaque table
SELECT 
    'traffic_data' as table_name, 
    COUNT(*) as total_records
FROM traffic_data
UNION ALL
SELECT 
    'public_transport', 
    COUNT(*)
FROM public_transport
UNION ALL
SELECT 
    'taxi_data', 
    COUNT(*)
FROM taxi_data;
