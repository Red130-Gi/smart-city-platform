"""
Script de validation Big Data - Apache Spark
Tests du pipeline de streaming et de traitement
"""

import subprocess
import time
import json
from datetime import datetime
import requests

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_spark_container():
    """Vérifie si le container Spark est en cours d'exécution"""
    print_header("🔍 VÉRIFICATION CONTAINER SPARK")
    
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=spark', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        containers = result.stdout.strip().split('\n')
        spark_containers = [c for c in containers if c and 'spark' in c.lower()]
        
        if spark_containers:
            print(f"✅ Containers Spark trouvés: {len(spark_containers)}")
            for container in spark_containers:
                print(f"   - {container}")
            return True
        else:
            print("❌ Aucun container Spark trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_spark_logs():
    """Analyse les logs Spark"""
    print_header("📋 ANALYSE DES LOGS SPARK")
    
    try:
        # Récupérer les logs récents
        result = subprocess.run(
            ['docker', 'logs', '--tail', '100', 'smart-city-spark'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        logs = result.stdout + result.stderr
        
        # Vérifier les indicateurs clés
        indicators = {
            'Spark Context': 'sparkcontext' in logs.lower() or 'spark context' in logs.lower(),
            'Streaming': 'streaming' in logs.lower(),
            'Kafka': 'kafka' in logs.lower(),
            'Processing': 'processing' in logs.lower() or 'batch' in logs.lower(),
            'Errors': 'error' in logs.lower() or 'exception' in logs.lower()
        }
        
        print("\nIndicateurs trouvés:")
        for indicator, found in indicators.items():
            status = "✅" if found else ("❌" if indicator != "Errors" else "✅")
            if indicator == "Errors":
                status = "⚠️" if found else "✅"
            print(f"  {status} {indicator}: {'Oui' if found else 'Non'}")
        
        # Afficher les dernières lignes importantes
        print("\nDernières activités:")
        lines = logs.split('\n')
        important_lines = [
            line for line in lines[-20:] 
            if any(keyword in line.lower() for keyword in ['batch', 'processing', 'completed', 'started', 'streaming'])
        ]
        
        for line in important_lines[-5:]:
            print(f"  {line[:100]}")
        
        return not indicators['Errors']
        
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout lors de la récupération des logs")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_kafka_topics():
    """Vérifie les topics Kafka"""
    print_header("📨 VÉRIFICATION KAFKA TOPICS")
    
    try:
        result = subprocess.run(
            ['docker', 'exec', 'smart-city-kafka', 
             'kafka-topics', '--list', '--bootstrap-server', 'localhost:9092'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            topics = result.stdout.strip().split('\n')
            topics = [t for t in topics if t]
            
            print(f"✅ Topics Kafka trouvés: {len(topics)}")
            for topic in topics:
                print(f"   - {topic}")
            
            # Vérifier les topics essentiels
            essential_topics = ['traffic-events', 'predictions', 'anomalies']
            missing_topics = [t for t in essential_topics if t not in topics]
            
            if missing_topics:
                print(f"\n⚠️ Topics manquants: {', '.join(missing_topics)}")
            else:
                print("\n✅ Tous les topics essentiels sont présents")
            
            return len(topics) > 0
        else:
            print(f"❌ Erreur Kafka: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def check_kafka_messages():
    """Vérifie les messages dans les topics Kafka"""
    print_header("📊 VÉRIFICATION MESSAGES KAFKA")
    
    topics_to_check = ['traffic-events', 'predictions']
    
    for topic in topics_to_check:
        try:
            print(f"\nTopic: {topic}")
            result = subprocess.run(
                ['docker', 'exec', 'smart-city-kafka',
                 'kafka-console-consumer', '--bootstrap-server', 'localhost:9092',
                 '--topic', topic, '--max-messages', '5', '--timeout-ms', '5000'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                messages = result.stdout.strip().split('\n')
                print(f"  ✅ {len(messages)} messages récents")
                
                # Afficher un exemple de message
                if messages:
                    try:
                        sample = json.loads(messages[0])
                        print(f"  📄 Exemple: {json.dumps(sample, indent=2)[:200]}...")
                    except:
                        print(f"  📄 Exemple: {messages[0][:100]}...")
            else:
                print(f"  ⚠️ Aucun message récent")
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ Timeout - topic peut être vide")
        except Exception as e:
            print(f"  ⚠️ Erreur: {e}")

def check_streaming_jobs():
    """Vérifie les jobs Spark Streaming"""
    print_header("⚡ VÉRIFICATION SPARK STREAMING JOBS")
    
    try:
        # Essayer d'accéder à l'UI Spark
        spark_ui_url = "http://localhost:4040/api/v1/applications"
        
        try:
            response = requests.get(spark_ui_url, timeout=5)
            
            if response.status_code == 200:
                apps = response.json()
                print(f"✅ Applications Spark actives: {len(apps)}")
                
                for app in apps:
                    print(f"\n  Application: {app.get('name', 'Unknown')}")
                    print(f"    ID: {app.get('id', 'N/A')}")
                    print(f"    Statut: {app.get('attempts', [{}])[0].get('completed', False)}")
                
                return True
            else:
                print("⚠️ Spark UI non accessible (normal si pas de jobs actifs)")
                return False
                
        except requests.ConnectionError:
            print("⚠️ Spark UI non accessible sur le port 4040")
            print("   (Normal si aucun job n'est en cours)")
            return False
            
    except Exception as e:
        print(f"⚠️ Impossible de vérifier les jobs: {e}")
        return False

def check_data_processing():
    """Vérifie que les données sont traitées"""
    print_header("🔄 VÉRIFICATION TRAITEMENT DES DONNÉES")
    
    try:
        # Vérifier dans PostgreSQL si les données sont récentes
        result = subprocess.run(
            ['docker', 'exec', 'smart-city-postgres',
             'psql', '-U', 'smartcity', '-d', 'smartcitydb',
             '-c', "SELECT COUNT(*) FROM traffic_data WHERE timestamp > NOW() - INTERVAL '5 minutes'"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extraire le nombre
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip().isdigit():
                    count = int(line.strip())
                    print(f"✅ Données récentes (5 dernières minutes): {count} enregistrements")
                    
                    if count > 0:
                        print("✅ Le pipeline traite activement les données")
                        return True
                    else:
                        print("⚠️ Aucune donnée récente détectée")
                        return False
        else:
            print("⚠️ Impossible de vérifier les données récentes")
            return False
            
    except Exception as e:
        print(f"⚠️ Erreur: {e}")
        return False

def check_spark_metrics():
    """Vérifie les métriques Spark"""
    print_header("📈 MÉTRIQUES SPARK")
    
    try:
        # Récupérer les stats du container
        result = subprocess.run(
            ['docker', 'stats', '--no-stream', '--format',
             '{{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}',
             'smart-city-spark'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            stats = result.stdout.strip().split('\t')
            if len(stats) >= 3:
                print(f"Container: {stats[0]}")
                print(f"  CPU: {stats[1]}")
                print(f"  Mémoire: {stats[2]}")
                
                # Vérifier si le CPU est actif
                cpu_val = float(stats[1].replace('%', ''))
                if cpu_val > 0.5:
                    print("✅ Spark est actif (CPU > 0.5%)")
                    return True
                else:
                    print("⚠️ Spark semble inactif (CPU très faible)")
                    return False
        else:
            print("⚠️ Impossible de récupérer les métriques")
            return False
            
    except Exception as e:
        print(f"⚠️ Erreur: {e}")
        return False

def generate_report(results):
    """Génère un rapport de validation"""
    print_header("📊 RAPPORT DE VALIDATION BIG DATA")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\nTests exécutés: {total_checks}")
    print(f"Tests réussis: {passed_checks}")
    print(f"Taux de réussite: {success_rate:.1f}%")
    
    print("\nDétails:")
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    print("\n" + "="*70)
    
    if success_rate >= 80:
        print("✅ PLATEFORME BIG DATA OPÉRATIONNELLE")
    elif success_rate >= 50:
        print("⚠️ PLATEFORME BIG DATA PARTIELLEMENT OPÉRATIONNELLE")
    else:
        print("❌ PROBLÈMES CRITIQUES DÉTECTÉS")
    
    print("="*70)
    
    # Sauvegarder le rapport
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_checks': total_checks,
        'passed_checks': passed_checks,
        'success_rate': success_rate,
        'details': results
    }
    
    try:
        with open('docs/BIGDATA_VALIDATION_REPORT.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("\n💾 Rapport sauvegardé: docs/BIGDATA_VALIDATION_REPORT.json")
    except Exception as e:
        print(f"\n⚠️ Erreur sauvegarde: {e}")

def main():
    """Fonction principale"""
    print("\n" + "="*70)
    print("  🧪 VALIDATION BIG DATA - APACHE SPARK")
    print("="*70)
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Exécuter les vérifications
    results = {
        'Spark Container': check_spark_container(),
        'Spark Logs': check_spark_logs(),
        'Kafka Topics': check_kafka_topics(),
        'Data Processing': check_data_processing(),
        'Spark Metrics': check_spark_metrics()
    }
    
    # Vérifications supplémentaires
    check_kafka_messages()
    check_streaming_jobs()
    
    # Générer le rapport
    generate_report(results)

if __name__ == "__main__":
    main()
