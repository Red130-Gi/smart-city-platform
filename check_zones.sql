-- Vérifier les zones disponibles
SELECT DISTINCT zone_id FROM traffic_data WHERE zone_id IS NOT NULL ORDER BY zone_id LIMIT 10;

-- Vérifier prédictions avec zones
SELECT DISTINCT zone_id FROM traffic_predictions WHERE zone_id IS NOT NULL;
