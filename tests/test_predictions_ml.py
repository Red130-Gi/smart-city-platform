"""
Tests pour les fonctionnalités de prédiction ML
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_future_traffic_predictions():
    """Test des prédictions de trafic futur"""
    print("\n🔮 Test: Future Traffic Predictions")
    print("-" * 50)
    
    zones = ["zone-1", "zone-2", "zone-3", "zone-4", "zone-5"]
    
    for zone in zones:
        response = requests.get(
            f"{BASE_URL}/predict/traffic/future",
            params={
                "zone_id": zone,
                "horizon_hours": 24,
                "interval_minutes": 60
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Zone {zone}:")
            print(f"   - Prédictions: {len(data['predictions'])}")
            print(f"   - Vitesse moyenne: {data['statistics']['avg_speed']:.1f} km/h")
            print(f"   - Périodes congestionnées: {data['statistics']['congestion_periods']}")
            
            # Afficher la première prédiction
            if data['predictions']:
                first = data['predictions'][0]
                print(f"   - Première prédiction: {first['predicted_speed_kmh']:.1f} km/h")
                print(f"   - Niveau: {first['congestion_level']}")
                print(f"   - Confiance: {first['confidence']:.2f}")
        else:
            print(f"❌ Erreur zone {zone}: {response.status_code}")

def test_multizone_predictions():
    """Test des prédictions multi-zones"""
    print("\n🌍 Test: Multi-Zone Predictions")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/predict/traffic/multizone",
        params={
            "zones": "zone-1,zone-2,zone-3,zone-4,zone-5",
            "target_time": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Prédictions pour {len(data['zones'])} zones")
        
        for zone in data['zones']:
            status = "🟢" if zone['congestion_level'] == "low" else "🟡" if zone['congestion_level'] == "medium" else "🔴"
            print(f"   {status} {zone['zone_name']}: {zone['predicted_speed_kmh']:.1f} km/h ({zone['congestion_level']})")
        
        print(f"\n📊 Statut global: {data['city_wide_status']['status']}")
        print(f"   - Indice mobilité: {data['city_wide_status']['mobility_index']:.1f}%")
    else:
        print(f"❌ Erreur: {response.status_code}")

def test_optimal_route():
    """Test de recommandation de route optimale"""
    print("\n🚗 Test: Optimal Route Recommendation")
    print("-" * 50)
    
    origins = ["zone-1", "zone-2"]
    destinations = ["zone-3", "zone-5"]
    
    for origin in origins:
        for dest in destinations:
            response = requests.get(
                f"{BASE_URL}/predict/route/optimal",
                params={
                    "origin_zone": origin,
                    "destination_zone": dest,
                    "modes": "car,bus,bike,walk"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Route {origin} → {dest}:")
                
                for route in data['routes']:
                    emoji = "🚗" if route['mode'] == "car" else "🚌" if route['mode'] == "bus" else "🚲" if route['mode'] == "bike" else "🚶"
                    recommended = "⭐" if route.get('recommended') else ""
                    print(f"   {emoji} {route['mode']}: {route['duration_minutes']:.1f} min, {route['carbon_g']}g CO₂ {recommended}")
                
                print(f"   💡 Meilleure option: {data['best_option']}")
                print(f"   ⏱️ Temps économisé: {data['time_saved']:.1f} min")
                print(f"   🌱 CO₂ économisé: {data['carbon_saved']}g\n")
            else:
                print(f"❌ Erreur route {origin}→{dest}: {response.status_code}")

def test_anomaly_detection():
    """Test de détection d'anomalies"""
    print("\n🚨 Test: Anomaly Detection")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/predict/anomalies",
        params={
            "zone_id": "all",
            "threshold": 0.7
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Scan complété")
        print(f"   - Anomalies détectées: {data['anomalies_detected']}")
        print(f"   - Statut système: {data['system_status']}")
        
        if data['anomalies']:
            print("\n   Détails des anomalies:")
            for anomaly in data['anomalies'][:5]:  # Afficher max 5
                severity_emoji = "🔴" if anomaly['severity'] == "high" else "🟡"
                print(f"   {severity_emoji} {anomaly['zone_id']} dans {anomaly['hours_ahead']}h")
                print(f"      Type: {anomaly['anomaly_type']}")
                print(f"      Action: {anomaly['recommended_action']}")
        
        if data['alerts']:
            print("\n   ⚠️ Alertes générées:")
            for alert in data['alerts']:
                print(f"      - {alert['message']}")
                print(f"        Action: {alert['action']}")
    else:
        print(f"❌ Erreur: {response.status_code}")

def test_api_performance():
    """Test de performance de l'API"""
    print("\n⚡ Test: API Performance")
    print("-" * 50)
    
    endpoints = [
        ("/predict/traffic/future?zone_id=zone-1&horizon_hours=1", "Future Traffic"),
        ("/predict/traffic/multizone?zones=zone-1,zone-2", "Multi-zone"),
        ("/predict/route/optimal?origin_zone=zone-1&destination_zone=zone-2", "Route Optimal"),
        ("/predict/anomalies?zone_id=zone-1", "Anomalies")
    ]
    
    for endpoint, name in endpoints:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}")
        latency = (time.time() - start_time) * 1000
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {name}: {latency:.0f}ms")
        
        if response.status_code == 200:
            data_size = len(json.dumps(response.json()))
            print(f"      Response size: {data_size} bytes")

def test_model_info():
    """Test des informations sur les modèles ML"""
    print("\n🧠 Test: ML Model Information")
    print("-" * 50)
    
    response = requests.get(
        f"{BASE_URL}/predict/traffic/future",
        params={
            "zone_id": "zone-1",
            "horizon_hours": 1,
            "interval_minutes": 60
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'model_info' in data:
            model = data['model_info']
            print(f"✅ Modèle actif:")
            print(f"   - Type: {model['type']}")
            print(f"   - Précision: {model['accuracy'] * 100:.0f}%")
            print(f"   - Dernière mise à jour: {model['last_trained']}")
        
        # Afficher les composants du modèle ensemble
        if data['predictions'] and 'components' in data['predictions'][0]:
            print("\n   Composants ensemble:")
            for component, value in data['predictions'][0]['components'].items():
                print(f"   - {component}: {value:.2f} km/h")
    else:
        print(f"❌ Erreur: {response.status_code}")

def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "="*60)
    print("🧪 TESTS DES PRÉDICTIONS ML - SMART CITY PLATFORM")
    print("="*60)
    
    tests = [
        test_future_traffic_predictions,
        test_multizone_predictions,
        test_optimal_route,
        test_anomaly_detection,
        test_api_performance,
        test_model_info
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n❌ Erreur dans {test.__name__}: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTS TERMINÉS")
    print("="*60)

if __name__ == "__main__":
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{BASE_URL[:-7]}/health")
        if response.status_code == 200:
            print("✅ API accessible")
            run_all_tests()
        else:
            print(f"⚠️ API retourne le code {response.status_code}")
    except requests.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("   Assurez-vous que l'API est démarrée avec:")
        print("   docker-compose up -d")
