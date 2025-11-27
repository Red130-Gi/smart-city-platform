-- ===============================================
-- Script de validation de la base de données
-- Smart City Platform - PostgreSQL
-- ===============================================

\echo '================================'
\echo 'VALIDATION BASE DE DONNÉES'
\echo '================================'

-- 1. Vérifier les tables existantes
\echo ''
\echo '[1] TABLES EXISTANTES'
\echo '--------------------'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 2. Compter les enregistrements par table
\echo ''
\echo '[2] NOMBRE D''ENREGISTREMENTS'
\echo '----------------------------'

DO $$ 
DECLARE
    table_record RECORD;
    row_count INTEGER;
BEGIN
    FOR table_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_record.tablename) INTO row_count;
        RAISE NOTICE '  % : % enregistrements', 
            RPAD(table_record.tablename, 30), 
            LPAD(row_count::TEXT, 10);
    END LOOP;
END $$;

-- 3. Vérifier les données de trafic
\echo ''
\echo '[3] DONNÉES DE TRAFIC'
\echo '--------------------'

-- Statistiques sur traffic_data
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT zone_id) as unique_zones,
    MIN(timestamp) as oldest_record,
    MAX(timestamp) as newest_record,
    COUNT(CASE WHEN timestamp > NOW() - INTERVAL '1 hour' THEN 1 END) as recent_records,
    ROUND(AVG(vehicle_count), 2) as avg_vehicle_count,
    ROUND(AVG(speed_kmh), 2) as avg_speed_kmh
FROM traffic_data
WHERE EXISTS (SELECT 1 FROM traffic_data LIMIT 1);

-- 4. Vérifier les zones
\echo ''
\echo '[4] ZONES CONFIGURÉES'
\echo '--------------------'

SELECT 
    zone_id,
    zone_name,
    zone_type,
    population,
    area_km2
FROM zones
ORDER BY zone_id;

-- 5. Vérifier les prédictions ML
\echo ''
\echo '[5] PRÉDICTIONS ML'
\echo '-----------------'

SELECT 
    COUNT(*) as total_predictions,
    COUNT(DISTINCT zone_id) as zones_with_predictions,
    MIN(prediction_time) as oldest_prediction,
    MAX(prediction_time) as newest_prediction,
    COUNT(CASE WHEN prediction_time > NOW() - INTERVAL '1 hour' THEN 1 END) as recent_predictions,
    ROUND(AVG(predicted_speed), 2) as avg_predicted_speed,
    ROUND(AVG(confidence_score), 3) as avg_confidence
FROM predictions
WHERE EXISTS (SELECT 1 FROM predictions LIMIT 1);

-- 6. Vérifier les trajets de taxis
\echo ''
\echo '[6] DONNÉES TAXIS'
\echo '----------------'

SELECT 
    COUNT(*) as total_trips,
    COUNT(DISTINCT taxi_id) as unique_taxis,
    COUNT(DISTINCT pickup_zone) as pickup_zones,
    COUNT(DISTINCT dropoff_zone) as dropoff_zones,
    ROUND(AVG(trip_distance_km), 2) as avg_distance_km,
    ROUND(AVG(trip_duration_minutes), 2) as avg_duration_min,
    ROUND(AVG(fare_amount), 2) as avg_fare
FROM taxi_trips
WHERE EXISTS (SELECT 1 FROM taxi_trips LIMIT 1);

-- 7. Qualité des données - Valeurs nulles
\echo ''
\echo '[7] QUALITÉ DES DONNÉES (Valeurs nulles)'
\echo '---------------------------------------'

SELECT 
    'traffic_data' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zone_id,
    COUNT(CASE WHEN speed_kmh IS NULL THEN 1 END) as null_speed,
    COUNT(CASE WHEN vehicle_count IS NULL THEN 1 END) as null_vehicle_count
FROM traffic_data
WHERE EXISTS (SELECT 1 FROM traffic_data LIMIT 1)
UNION ALL
SELECT 
    'predictions' as table_name,
    COUNT(*) as total_rows,
    COUNT(CASE WHEN zone_id IS NULL THEN 1 END) as null_zone_id,
    COUNT(CASE WHEN predicted_speed IS NULL THEN 1 END) as null_predicted_speed,
    COUNT(CASE WHEN confidence_score IS NULL THEN 1 END) as null_confidence
FROM predictions
WHERE EXISTS (SELECT 1 FROM predictions LIMIT 1);

-- 8. Distribution temporelle des données
\echo ''
\echo '[8] DISTRIBUTION TEMPORELLE'
\echo '--------------------------'

SELECT 
    date_trunc('hour', timestamp) as hour,
    COUNT(*) as record_count,
    COUNT(DISTINCT zone_id) as zones_active,
    ROUND(AVG(speed_kmh), 2) as avg_speed,
    ROUND(AVG(vehicle_count), 2) as avg_vehicles
FROM traffic_data
WHERE timestamp > NOW() - INTERVAL '24 hours'
  AND EXISTS (SELECT 1 FROM traffic_data LIMIT 1)
GROUP BY date_trunc('hour', timestamp)
ORDER BY hour DESC
LIMIT 24;

-- 9. Top zones par activité
\echo ''
\echo '[9] TOP 10 ZONES PAR ACTIVITÉ'
\echo '-----------------------------'

SELECT 
    z.zone_id,
    z.zone_name,
    COUNT(t.id) as data_points,
    ROUND(AVG(t.speed_kmh), 2) as avg_speed,
    ROUND(AVG(t.vehicle_count), 2) as avg_vehicles,
    ROUND(AVG(t.congestion_level), 2) as avg_congestion
FROM zones z
LEFT JOIN traffic_data t ON z.zone_id = t.zone_id
WHERE EXISTS (SELECT 1 FROM traffic_data LIMIT 1)
GROUP BY z.zone_id, z.zone_name
ORDER BY data_points DESC
LIMIT 10;

-- 10. Vérification des contraintes et index
\echo ''
\echo '[10] INDEX ET CONTRAINTES'
\echo '------------------------'

SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- 11. Performance des requêtes
\echo ''
\echo '[11] STATISTIQUES DE PERFORMANCE'
\echo '--------------------------------'

SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

-- 12. Résumé de validation
\echo ''
\echo '[12] RÉSUMÉ DE VALIDATION'
\echo '------------------------'

DO $$ 
DECLARE
    traffic_count INTEGER;
    prediction_count INTEGER;
    zone_count INTEGER;
    taxi_count INTEGER;
    validation_status TEXT;
BEGIN
    SELECT COUNT(*) INTO traffic_count FROM traffic_data;
    SELECT COUNT(*) INTO prediction_count FROM predictions;
    SELECT COUNT(*) INTO zone_count FROM zones;
    SELECT COUNT(*) INTO taxi_count FROM taxi_trips;
    
    IF traffic_count > 0 AND zone_count > 0 THEN
        validation_status := '✅ BASE DE DONNÉES OPÉRATIONNELLE';
    ELSE
        validation_status := '❌ BASE DE DONNÉES INCOMPLÈTE';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE 'STATUT: %', validation_status;
    RAISE NOTICE '';
    RAISE NOTICE 'Données de trafic: %', traffic_count;
    RAISE NOTICE 'Prédictions ML: %', prediction_count;
    RAISE NOTICE 'Zones configurées: %', zone_count;
    RAISE NOTICE 'Trajets taxis: %', taxi_count;
    RAISE NOTICE '';
    
    IF traffic_count > 1000 THEN
        RAISE NOTICE '✅ Volume de données suffisant';
    ELSE
        RAISE NOTICE '⚠️  Volume de données faible';
    END IF;
    
    IF prediction_count > 0 THEN
        RAISE NOTICE '✅ Prédictions ML actives';
    ELSE
        RAISE NOTICE '⚠️  Aucune prédiction ML';
    END IF;
END $$;

\echo ''
\echo '================================'
\echo 'VALIDATION TERMINÉE'
\echo '================================'
