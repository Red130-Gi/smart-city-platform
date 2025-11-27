"""
Script de validation complète de la plateforme Smart City
Tests: Infrastructure, Données, ML, Big Data, Dashboards
"""

import sys
import time
import json
import requests
from datetime import datetime
import subprocess
import psycopg2
from pymongo import MongoClient

# Configuration
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'smartcitydb',
    'user': 'smartcity',
    'password': 'smartcity123'
}

MONGODB_CONFIG = {
    'host': 'localhost',
    'port': 27017
}

API_BASE_URL = "http://localhost:8000/api/v1"
GRAFANA_URL = "http://localhost:3000"

# Résultats globaux
test_results = {
    'timestamp': datetime.now().isoformat(),
    'infrastructure': {},
    'database': {},
    'bigdata': {},
    'ml': {},
    'api': {},
    'dashboards': {},
    'summary': {}
}

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_docker_services():
    """Test de l'infrastructure Docker"""
    print_section("🐳 TEST INFRASTRUCTURE DOCKER")
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        services = result.stdout.strip().split('\n')
        
        expected_services = [
            'postgres', 'mongodb', 'redis', 'kafka', 
            'zookeeper', 'grafana', 'api'
        ]
        
        running_services = []
        for expected in expected_services:
            found = any(expected in service for service in services)
            status = "✅" if found else "❌"
            print(f"  {status} {expected.capitalize()}: {'Running' if found else 'Not found'}")
            if found:
                running_services.append(expected)
        
        test_results['infrastructure'] = {
            'expected': len(expected_services),
            'running': len(running_services),
            'services': running_services,
            'status': 'PASS' if len(running_services) >= 5 else 'PARTIAL'
        }
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        test_results['infrastructure']['status'] = 'FAIL'

def test_postgresql():
    """Test de PostgreSQL et données"""
    print_section("🗄️ TEST POSTGRESQL")
    
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        # Test connexion
        print("  ✅ Connexion PostgreSQL établie")
        
        # Vérifier les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        print(f"  📊 Tables trouvées: {len(table_names)}")
        for table in table_names:
            print(f"     - {table}")
        
        # Compter les enregistrements dans les tables principales
        main_tables = ['traffic_data', 'predictions', 'zones', 'taxi_trips']
        table_counts = {}
        
        for table in main_tables:
            if table in table_names:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts[table] = count
                print(f"  📈 {table}: {count:,} enregistrements")
        
        # Vérifier les données récentes
        if 'traffic_data' in table_names:
            cursor.execute("""
                SELECT COUNT(*) FROM traffic_data 
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            recent = cursor.fetchone()[0]
            print(f"  🕐 Données dernière heure: {recent:,} enregistrements")
        
        cursor.close()
        conn.close()
        
        test_results['database']['postgresql'] = {
            'status': 'PASS',
            'tables': len(table_names),
            'table_names': table_names,
            'records': table_counts
        }
        
    except Exception as e:
        print(f"  ❌ Erreur PostgreSQL: {e}")
        test_results['database']['postgresql'] = {
            'status': 'FAIL',
            'error': str(e)
        }

def test_mongodb():
    """Test de MongoDB"""
    print_section("🍃 TEST MONGODB")
    
    try:
        client = MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'])
        db = client['smartcity']
        
        print("  ✅ Connexion MongoDB établie")
        
        # Lister les collections
        collections = db.list_collection_names()
        print(f"  📊 Collections: {len(collections)}")
        
        collection_counts = {}
        for coll_name in collections:
            count = db[coll_name].count_documents({})
            collection_counts[coll_name] = count
            print(f"     - {coll_name}: {count:,} documents")
        
        client.close()
        
        test_results['database']['mongodb'] = {
            'status': 'PASS',
            'collections': len(collections),
            'documents': collection_counts
        }
        
    except Exception as e:
        print(f"  ❌ Erreur MongoDB: {e}")
        test_results['database']['mongodb'] = {
            'status': 'FAIL',
            'error': str(e)
        }

def test_spark_streaming():
    """Test du pipeline Spark"""
    print_section("⚡ TEST SPARK STREAMING")
    
    try:
        # Vérifier si Spark est en cours d'exécution
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if 'spark' in result.stdout.lower():
            print("  ✅ Spark container actif")
            
            # Vérifier les logs Spark
            result = subprocess.run(
                ['docker', 'logs', '--tail', '50', 'smart-city-spark'],
                capture_output=True, text=True
            )
            
            if 'streaming' in result.stdout.lower() or 'started' in result.stdout.lower():
                print("  ✅ Spark Streaming opérationnel")
                test_results['bigdata']['spark'] = {'status': 'PASS'}
            else:
                print("  ⚠️ Spark en cours de démarrage")
                test_results['bigdata']['spark'] = {'status': 'PARTIAL'}
        else:
            print("  ❌ Spark container non trouvé")
            test_results['bigdata']['spark'] = {'status': 'FAIL'}
            
    except Exception as e:
        print(f"  ❌ Erreur Spark: {e}")
        test_results['bigdata']['spark'] = {'status': 'FAIL', 'error': str(e)}

def test_ml_models():
    """Test des modèles ML"""
    print_section("🧠 TEST MODÈLES ML")
    
    try:
        # Test prédiction simple
        response = requests.get(
            f"{API_BASE_URL}/predict/traffic/future",
            params={
                'zone_id': 'zone-1',
                'horizon_hours': 1
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ API ML accessible")
            print(f"  📊 Prédictions générées: {len(data.get('predictions', []))}")
            
            if 'model_info' in data:
                model = data['model_info']
                print(f"  🎯 Modèle: {model.get('type', 'Unknown')}")
                print(f"  🎯 Précision: {model.get('accuracy', 0) * 100:.1f}%")
            
            test_results['ml']['predictions'] = {
                'status': 'PASS',
                'predictions_count': len(data.get('predictions', [])),
                'model_info': data.get('model_info', {})
            }
        else:
            print(f"  ❌ API retourne {response.status_code}")
            test_results['ml']['predictions'] = {'status': 'FAIL'}
            
    except requests.ConnectionError:
        print("  ❌ API ML non accessible")
        test_results['ml']['predictions'] = {'status': 'FAIL', 'error': 'Connection failed'}
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        test_results['ml']['predictions'] = {'status': 'FAIL', 'error': str(e)}

def test_api_endpoints():
    """Test des endpoints API"""
    print_section("🔌 TEST API ENDPOINTS")
    
    endpoints = [
        ('/health', 'Health Check'),
        ('/api/v1/zones', 'Zones'),
        ('/api/v1/traffic/current', 'Traffic Current'),
        ('/api/v1/predict/traffic/future?zone_id=zone-1&horizon_hours=1', 'Predictions')
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            url = f"http://localhost:8000{endpoint}"
            start = time.time()
            response = requests.get(url, timeout=5)
            latency = (time.time() - start) * 1000
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"  {status} {name}: {response.status_code} ({latency:.0f}ms)")
            
            results.append({
                'endpoint': name,
                'status_code': response.status_code,
                'latency_ms': latency,
                'success': response.status_code == 200
            })
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results.append({
                'endpoint': name,
                'error': str(e),
                'success': False
            })
    
    test_results['api'] = {
        'endpoints_tested': len(endpoints),
        'endpoints_passed': sum(1 for r in results if r.get('success')),
        'results': results
    }

def test_grafana():
    """Test de Grafana"""
    print_section("📊 TEST GRAFANA DASHBOARDS")
    
    try:
        # Test health
        response = requests.get(f"{GRAFANA_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            print("  ✅ Grafana accessible")
            
            # Essayer de lister les dashboards (nécessite auth)
            try:
                response = requests.get(
                    f"{GRAFANA_URL}/api/search?type=dash-db",
                    auth=('admin', 'admin'),
                    timeout=5
                )
                
                if response.status_code == 200:
                    dashboards = response.json()
                    print(f"  📊 Dashboards configurés: {len(dashboards)}")
                    for dash in dashboards:
                        print(f"     - {dash['title']}")
                    
                    test_results['dashboards'] = {
                        'status': 'PASS',
                        'count': len(dashboards),
                        'dashboards': [d['title'] for d in dashboards]
                    }
                else:
                    print(f"  ⚠️ Impossible de lister les dashboards: {response.status_code}")
                    test_results['dashboards'] = {'status': 'PARTIAL'}
            except:
                print("  ⚠️ Authentification requise pour les dashboards")
                test_results['dashboards'] = {'status': 'PARTIAL'}
        else:
            print(f"  ❌ Grafana retourne {response.status_code}")
            test_results['dashboards'] = {'status': 'FAIL'}
            
    except Exception as e:
        print(f"  ❌ Erreur Grafana: {e}")
        test_results['dashboards'] = {'status': 'FAIL', 'error': str(e)}

def generate_summary():
    """Génère le résumé des tests"""
    print_section("📝 RÉSUMÉ DES TESTS")
    
    total_tests = 0
    passed_tests = 0
    
    # Compter les tests
    for category, results in test_results.items():
        if category == 'summary' or category == 'timestamp':
            continue
        
        if isinstance(results, dict):
            if 'status' in results:
                total_tests += 1
                if results['status'] == 'PASS':
                    passed_tests += 1
            else:
                for key, value in results.items():
                    if isinstance(value, dict) and 'status' in value:
                        total_tests += 1
                        if value['status'] == 'PASS':
                            passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n  Tests exécutés: {total_tests}")
    print(f"  Tests réussis: {passed_tests}")
    print(f"  Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n  ✅ Plateforme opérationnelle")
        status = "OPERATIONAL"
    elif success_rate >= 50:
        print("\n  ⚠️ Plateforme partiellement opérationnelle")
        status = "PARTIAL"
    else:
        print("\n  ❌ Problèmes critiques détectés")
        status = "CRITICAL"
    
    test_results['summary'] = {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': success_rate,
        'status': status
    }

def save_report():
    """Sauvegarde le rapport de validation"""
    report_path = 'docs/VALIDATION_REPORT.json'
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        print(f"\n  💾 Rapport sauvegardé: {report_path}")
    except Exception as e:
        print(f"\n  ⚠️ Erreur sauvegarde rapport: {e}")

def generate_markdown_report():
    """Génère un rapport Markdown"""
    report_md = f"""# 🧪 Rapport de Validation - Smart City Platform

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Résumé Exécutif

- **Tests exécutés:** {test_results['summary']['total_tests']}
- **Tests réussis:** {test_results['summary']['passed_tests']}
- **Taux de réussite:** {test_results['summary']['success_rate']:.1f}%
- **Statut global:** {test_results['summary']['status']}

---

## 🐳 Infrastructure Docker

**Statut:** {test_results['infrastructure'].get('status', 'N/A')}

Services en cours d'exécution: {test_results['infrastructure'].get('running', 0)}/{test_results['infrastructure'].get('expected', 0)}

### Services actifs:
"""
    
    for service in test_results['infrastructure'].get('services', []):
        report_md += f"- ✅ {service.capitalize()}\n"
    
    report_md += """
---

## 🗄️ Bases de Données

### PostgreSQL
"""
    
    pg = test_results['database'].get('postgresql', {})
    if pg.get('status') == 'PASS':
        report_md += f"""
**Statut:** ✅ PASS

- Tables: {pg.get('tables', 0)}
- Enregistrements par table:
"""
        for table, count in pg.get('records', {}).items():
            report_md += f"  - `{table}`: {count:,}\n"
    else:
        report_md += f"**Statut:** ❌ FAIL\n"
    
    report_md += """
### MongoDB
"""
    
    mongo = test_results['database'].get('mongodb', {})
    if mongo.get('status') == 'PASS':
        report_md += f"""
**Statut:** ✅ PASS

- Collections: {mongo.get('collections', 0)}
"""
        for coll, count in mongo.get('documents', {}).items():
            report_md += f"  - `{coll}`: {count:,}\n"
    else:
        report_md += f"**Statut:** ❌ FAIL\n"
    
    report_md += """
---

## ⚡ Big Data (Spark)

"""
    
    spark = test_results['bigdata'].get('spark', {})
    report_md += f"**Statut:** {spark.get('status', 'N/A')}\n\n"
    
    report_md += """
---

## 🧠 Machine Learning

"""
    
    ml = test_results['ml'].get('predictions', {})
    if ml.get('status') == 'PASS':
        report_md += f"""
**Statut:** ✅ PASS

- Prédictions générées: {ml.get('predictions_count', 0)}
- Modèle: {ml.get('model_info', {}).get('type', 'N/A')}
"""
    else:
        report_md += f"**Statut:** ❌ FAIL\n"
    
    report_md += """
---

## 🔌 API Endpoints

"""
    
    api_results = test_results['api'].get('results', [])
    passed = sum(1 for r in api_results if r.get('success'))
    total = len(api_results)
    
    report_md += f"**Tests réussis:** {passed}/{total}\n\n"
    
    for result in api_results:
        status_icon = "✅" if result.get('success') else "❌"
        endpoint = result['endpoint']
        latency = result.get('latency_ms', 'N/A')
        report_md += f"- {status_icon} {endpoint}"
        if latency != 'N/A':
            report_md += f" ({latency:.0f}ms)"
        report_md += "\n"
    
    report_md += """
---

## 📊 Dashboards Grafana

"""
    
    dashboards = test_results.get('dashboards', {})
    if dashboards.get('status') == 'PASS':
        report_md += f"""
**Statut:** ✅ PASS

Dashboards configurés: {dashboards.get('count', 0)}

"""
        for dash in dashboards.get('dashboards', []):
            report_md += f"- {dash}\n"
    else:
        report_md += f"**Statut:** {dashboards.get('status', 'N/A')}\n"
    
    report_md += """
---

## 🎯 Recommandations

"""
    
    if test_results['summary']['success_rate'] >= 80:
        report_md += """
✅ La plateforme est opérationnelle et prête pour la production.

### Actions recommandées:
- Monitorer les performances en continu
- Vérifier les logs régulièrement
- Mettre en place des alertes automatiques
"""
    elif test_results['summary']['success_rate'] >= 50:
        report_md += """
⚠️ La plateforme est partiellement opérationnelle.

### Actions prioritaires:
- Corriger les services défaillants
- Vérifier les configurations
- Redémarrer les services problématiques
"""
    else:
        report_md += """
❌ Problèmes critiques détectés.

### Actions urgentes:
- Vérifier Docker Desktop
- Reconstruire les images Docker
- Consulter les logs détaillés
- Vérifier les configurations réseau
"""
    
    report_md += f"""
---

*Rapport généré automatiquement le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}*
"""
    
    try:
        with open('docs/VALIDATION_REPORT.md', 'w', encoding='utf-8') as f:
            f.write(report_md)
        print(f"  💾 Rapport Markdown sauvegardé: docs/VALIDATION_REPORT.md")
    except Exception as e:
        print(f"  ⚠️ Erreur sauvegarde rapport MD: {e}")

def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("  🧪 VALIDATION COMPLÈTE - SMART CITY PLATFORM")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Exécuter tous les tests
    test_docker_services()
    test_postgresql()
    test_mongodb()
    test_spark_streaming()
    test_ml_models()
    test_api_endpoints()
    test_grafana()
    
    # Générer le résumé
    generate_summary()
    
    # Sauvegarder les rapports
    save_report()
    generate_markdown_report()
    
    print("\n" + "="*70)
    print("  ✅ VALIDATION TERMINÉE")
    print("="*70)
    print("\n  📄 Rapports générés:")
    print("     - docs/VALIDATION_REPORT.json")
    print("     - docs/VALIDATION_REPORT.md")
    print("\n")

if __name__ == "__main__":
    main()
