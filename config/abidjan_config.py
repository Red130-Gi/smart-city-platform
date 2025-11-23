"""
Configuration géographique pour Abidjan, Côte d'Ivoire
Capitale économique avec ~5 millions d'habitants
"""

# Coordonnées GPS d'Abidjan
ABIDJAN_CENTER = {
    'lat': 5.3364,
    'lon': -4.0267
}

# 10 Communes d'Abidjan
COMMUNES = {
    'Plateau': {
        'lat': 5.3200,
        'lon': -4.0100,
        'type': 'centre_affaires',
        'population': 15000,
        'description': 'Centre administratif et financier'
    },
    'Cocody': {
        'lat': 5.3600,
        'lon': -3.9800,
        'type': 'residentiel_haut',
        'population': 400000,
        'description': 'Quartier résidentiel huppé, universités'
    },
    'Yopougon': {
        'lat': 5.3400,
        'lon': -4.0900,
        'type': 'residentiel_populaire',
        'population': 1200000,
        'description': 'Plus grande commune, très peuplée'
    },
    'Adjame': {
        'lat': 5.3500,
        'lon': -4.0200,
        'type': 'commercial',
        'population': 300000,
        'description': 'Grand marché, gare routière'
    },
    'Treichville': {
        'lat': 5.3000,
        'lon': -4.0000,
        'type': 'mixte',
        'population': 130000,
        'description': 'Port, quartier historique'
    },
    'Marcory': {
        'lat': 5.2800,
        'lon': -3.9700,
        'type': 'residentiel_mixte',
        'population': 250000,
        'description': 'Zone industrielle, résidentiel'
    },
    'Koumassi': {
        'lat': 5.3000,
        'lon': -3.9500,
        'type': 'industriel',
        'population': 450000,
        'description': 'Zone industrielle importante'
    },
    'Port-Bouet': {
        'lat': 5.2500,
        'lon': -3.9200,
        'type': 'aeroport',
        'population': 250000,
        'description': 'Aéroport international, plages'
    },
    'Attecoube': {
        'lat': 5.3300,
        'lon': -4.0500,
        'type': 'residentiel_populaire',
        'population': 300000,
        'description': 'Quartier populaire dense'
    },
    'Abobo': {
        'lat': 5.4200,
        'lon': -4.0200,
        'type': 'residentiel_populaire',
        'population': 1200000,
        'description': 'Très grande commune au nord'
    }
}

# 5 Zones de trafic stratégiques
ZONES_TRAFIC = {
    'zone-centre': {
        'name': 'Centre (Plateau-Adjamé)',
        'communes': ['Plateau', 'Adjame'],
        'lat': 5.335,
        'lon': -4.015,
        'congestion_level': 'tres_elevee',
        'rush_hours': ['07:00-09:30', '17:30-20:00']
    },
    'zone-nord': {
        'name': 'Nord (Abobo-Yopougon)',
        'communes': ['Abobo', 'Yopougon', 'Attecoube'],
        'lat': 5.38,
        'lon': -4.055,
        'congestion_level': 'elevee',
        'rush_hours': ['06:30-09:00', '17:00-20:00']
    },
    'zone-est': {
        'name': 'Est (Cocody-Koumassi)',
        'communes': ['Cocody', 'Koumassi'],
        'lat': 5.33,
        'lon': -3.965,
        'congestion_level': 'moyenne',
        'rush_hours': ['07:30-09:00', '17:30-19:30']
    },
    'zone-sud': {
        'name': 'Sud (Treichville-Marcory)',
        'communes': ['Treichville', 'Marcory', 'Port-Bouet'],
        'lat': 5.285,
        'lon': -3.96,
        'congestion_level': 'moyenne',
        'rush_hours': ['07:00-09:00', '17:00-19:00']
    },
    'zone-ouest': {
        'name': 'Ouest (Yopougon)',
        'communes': ['Yopougon'],
        'lat': 5.34,
        'lon': -4.09,
        'congestion_level': 'elevee',
        'rush_hours': ['06:00-09:30', '16:30-20:30']
    }
}

# Routes principales d'Abidjan
ROUTES_PRINCIPALES = [
    {
        'id': 'A1',
        'name': 'Boulevard Valéry Giscard d\'Estaing (VGE)',
        'type': 'autoroute',
        'start': {'lat': 5.42, 'lon': -4.02},
        'end': {'lat': 5.25, 'lon': -3.92},
        'communes': ['Abobo', 'Adjame', 'Plateau', 'Treichville', 'Port-Bouet'],
        'vitesse_max': 90,
        'voies': 4,
        'importance': 'tres_haute'
    },
    {
        'id': 'A2',
        'name': 'Autoroute du Nord',
        'type': 'autoroute',
        'start': {'lat': 5.35, 'lon': -4.02},
        'end': {'lat': 5.50, 'lon': -4.02},
        'communes': ['Adjame', 'Abobo'],
        'vitesse_max': 100,
        'voies': 4,
        'importance': 'tres_haute'
    },
    {
        'id': 'B1',
        'name': 'Boulevard Latrille',
        'type': 'boulevard',
        'start': {'lat': 5.34, 'lon': -4.09},
        'end': {'lat': 5.32, 'lon': -4.01},
        'communes': ['Yopougon', 'Attecoube', 'Plateau'],
        'vitesse_max': 70,
        'voies': 3,
        'importance': 'haute'
    },
    {
        'id': 'B2',
        'name': 'Boulevard de Marseille',
        'type': 'boulevard',
        'start': {'lat': 5.36, 'lon': -3.98},
        'end': {'lat': 5.30, 'lon': -3.95},
        'communes': ['Cocody', 'Marcory'],
        'vitesse_max': 70,
        'voies': 3,
        'importance': 'haute'
    },
    {
        'id': 'B3',
        'name': 'Boulevard Hassan II',
        'type': 'boulevard',
        'start': {'lat': 5.36, 'lon': -3.99},
        'end': {'lat': 5.35, 'lon': -3.96},
        'communes': ['Cocody'],
        'vitesse_max': 60,
        'voies': 2,
        'importance': 'moyenne'
    },
    {
        'id': 'P1',
        'name': 'Pont Houphouët-Boigny',
        'type': 'pont',
        'start': {'lat': 5.32, 'lon': -4.01},
        'end': {'lat': 5.30, 'lon': -4.00},
        'communes': ['Plateau', 'Treichville'],
        'vitesse_max': 50,
        'voies': 4,
        'importance': 'critique'
    },
    {
        'id': 'P2',
        'name': 'Pont Charles de Gaulle',
        'type': 'pont',
        'start': {'lat': 5.32, 'lon': -4.01},
        'end': {'lat': 5.30, 'lon': -3.99},
        'communes': ['Plateau', 'Treichville'],
        'vitesse_max': 50,
        'voies': 2,
        'importance': 'critique'
    },
    {
        'id': 'P3',
        'name': 'Pont Henri Konan Bédié (3e pont)',
        'type': 'pont',
        'start': {'lat': 5.34, 'lon': -4.00},
        'end': {'lat': 5.32, 'lon': -3.98},
        'communes': ['Cocody', 'Marcory'],
        'vitesse_max': 90,
        'voies': 6,
        'importance': 'critique'
    },
    {
        'id': 'R1',
        'name': 'Rue du Commerce (Treichville)',
        'type': 'rue',
        'start': {'lat': 5.30, 'lon': -4.00},
        'end': {'lat': 5.29, 'lon': -3.98},
        'communes': ['Treichville'],
        'vitesse_max': 50,
        'voies': 2,
        'importance': 'moyenne'
    },
    {
        'id': 'R2',
        'name': 'Rue Lecoeur (Plateau)',
        'type': 'rue',
        'start': {'lat': 5.32, 'lon': -4.01},
        'end': {'lat': 5.31, 'lon': -4.00},
        'communes': ['Plateau'],
        'vitesse_max': 40,
        'voies': 2,
        'importance': 'moyenne'
    }
]

# Points d'intérêt stratégiques
POINTS_INTERET = {
    'aeroport_abidjan': {
        'name': 'Aéroport International Félix Houphouët-Boigny',
        'lat': 5.2539,
        'lon': -3.9263,
        'commune': 'Port-Bouet',
        'type': 'aeroport'
    },
    'port_autonome': {
        'name': 'Port Autonome d\'Abidjan',
        'lat': 5.2800,
        'lon': -3.9900,
        'commune': 'Treichville',
        'type': 'port'
    },
    'gare_routiere_adjame': {
        'name': 'Gare Routière d\'Adjamé',
        'lat': 5.3550,
        'lon': -4.0200,
        'commune': 'Adjame',
        'type': 'transport'
    },
    'marche_adjame': {
        'name': 'Grand Marché d\'Adjamé',
        'lat': 5.3560,
        'lon': -4.0180,
        'commune': 'Adjame',
        'type': 'commercial'
    },
    'universite_cocody': {
        'name': 'Université Félix Houphouët-Boigny',
        'lat': 5.3700,
        'lon': -3.9800,
        'commune': 'Cocody',
        'type': 'education'
    },
    'stade_ebimpe': {
        'name': 'Stade Olympique Alassane Ouattara (Ebimpé)',
        'lat': 5.4700,
        'lon': -4.1500,
        'commune': 'Anyama',
        'type': 'sport'
    }
}

# Transport en commun
TRANSPORT_COMMUN = {
    'gbaka': {
        'name': 'Gbaka (minibus)',
        'capacite': 25,
        'tarif_moyen': 200,  # FCFA
        'vitesse_moyenne': 25
    },
    'woro_woro': {
        'name': 'Woro-woro (taxi communal)',
        'capacite': 7,
        'tarif_moyen': 300,  # FCFA
        'vitesse_moyenne': 30
    },
    'taxi': {
        'name': 'Taxi compteur',
        'capacite': 4,
        'tarif_base': 500,  # FCFA
        'vitesse_moyenne': 35
    },
    'bus_sotra': {
        'name': 'Bus SOTRA',
        'capacite': 100,
        'tarif': 150,  # FCFA
        'vitesse_moyenne': 20
    }
}

# Heures de pointe spécifiques à Abidjan
HEURES_POINTE = {
    'matin': {
        'debut': '06:00',
        'fin': '10:00',
        'pic': '07:30',
        'multiplicateur_trafic': 2.5
    },
    'midi': {
        'debut': '12:00',
        'fin': '14:00',
        'pic': '13:00',
        'multiplicateur_trafic': 1.4
    },
    'soir': {
        'debut': '16:30',
        'fin': '21:00',
        'pic': '18:30',
        'multiplicateur_trafic': 3.0  # Plus intense qu'au matin
    }
}

# Statistiques réelles Abidjan
STATS_ABIDJAN = {
    'population': 5000000,
    'superficie_km2': 422,
    'densite_hab_km2': 11848,
    'nb_vehicules_estimes': 800000,
    'taux_motorisation': 16,  # véhicules pour 100 habitants
    'vitesse_moyenne_jour': 25,  # km/h
    'vitesse_moyenne_pointe': 12,  # km/h
    'temps_trajet_moyen': 75,  # minutes
    'nb_accidents_annuels': 3500,
    'embouteillages_couts_annuels_milliards_fcfa': 150
}

def get_zone_from_commune(commune_name):
    """Retourne la zone de trafic correspondant à une commune"""
    for zone_id, zone_data in ZONES_TRAFIC.items():
        if commune_name in zone_data['communes']:
            return zone_id
    return 'zone-centre'  # Default

def get_random_location_in_commune(commune_name):
    """Génère des coordonnées aléatoires dans une commune"""
    import random
    if commune_name in COMMUNES:
        commune = COMMUNES[commune_name]
        # Variation de ±0.01 degrés (environ 1km)
        lat = commune['lat'] + random.uniform(-0.01, 0.01)
        lon = commune['lon'] + random.uniform(-0.01, 0.01)
        return lat, lon
    return ABIDJAN_CENTER['lat'], ABIDJAN_CENTER['lon']

def is_rush_hour(hour):
    """Vérifie si l'heure donnée est une heure de pointe"""
    if 6 <= hour < 10:
        return 'matin'
    elif 12 <= hour < 14:
        return 'midi'
    elif 16.5 <= hour < 21:
        return 'soir'
    return None
