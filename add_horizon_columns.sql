-- Ajouter colonnes multi-horizons à la table traffic_predictions

-- Ajouter horizon_min (délai en minutes)
ALTER TABLE traffic_predictions 
ADD COLUMN IF NOT EXISTS horizon_min INTEGER DEFAULT 5;

-- Ajouter horizon_type (court/moyen/long)
ALTER TABLE traffic_predictions 
ADD COLUMN IF NOT EXISTS horizon_type TEXT DEFAULT 'short';

-- Créer index pour performances
CREATE INDEX IF NOT EXISTS idx_traffic_predictions_horizon_type 
ON traffic_predictions (horizon_type);

CREATE INDEX IF NOT EXISTS idx_traffic_predictions_horizon_min 
ON traffic_predictions (horizon_min);

-- Vérifier colonnes ajoutées
\d traffic_predictions
