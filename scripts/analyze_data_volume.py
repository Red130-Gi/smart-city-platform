#!/usr/bin/env python3
"""
Analyse du volume de données pour validation Big Data
"""
import psycopg2
from datetime import datetime, timedelta

def analyze_data_volume():
    """Analyse le volume de données dans PostgreSQL"""
    
    conn = psycopg2.connect(
        host='localhost',
        dbname='smart_city_db',
        user='smart_city',
        password='smartcity123',
        port=5432
    )
    
    cursor = conn.cursor()
    
    print("="*70)
    print("ANALYSE DU VOLUME DE DONNÉES - SMART CITY PLATFORM")
    print("="*70)
    print()
    
    # Volume total par table
    tables = ['traffic_data', 'public_transport', 'parking_data']
    total_records = 0
    
    print("📊 VOLUME ACTUEL PAR TABLE")
    print("-"*70)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        
        cursor.execute(f"SELECT pg_size_pretty(pg_total_relation_size('{table}'))")
        size = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {table}")
        min_ts, max_ts = cursor.fetchone()
        
        if min_ts and max_ts:
            duration = max_ts - min_ts
            hours = duration.total_seconds() / 3600
            records_per_hour = count / hours if hours > 0 else 0
        else:
            hours = 0
            records_per_hour = 0
        
        print(f"  {table:20} : {count:>10,} records | {size:>10} | {records_per_hour:>8.0f} rec/h")
    
    print("-"*70)
    print(f"  {'TOTAL':20} : {total_records:>10,} records")
    print()
    
    # Calcul de la taille totale
    cursor.execute("SELECT pg_size_pretty(pg_database_size('smart_city_db'))")
    db_size = cursor.fetchone()[0]
    print(f"💾 Taille totale de la base : {db_size}")
    print()
    
    # Taux de génération actuel
    print("⚡ TAUX DE GÉNÉRATION ACTUEL")
    print("-"*70)
    
    # Données des 5 dernières minutes
    for table in tables:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {table} 
            WHERE timestamp > NOW() - INTERVAL '5 minutes'
        """)
        recent_count = cursor.fetchone()[0]
        per_minute = recent_count / 5
        per_hour = per_minute * 60
        per_day = per_hour * 24
        
        print(f"  {table:20} : {recent_count:>6} records/5min")
        print(f"                         → {per_minute:>6.0f} records/min")
        print(f"                         → {per_hour:>6.0f} records/hour")
        print(f"                         → {per_day:>8,.0f} records/day")
        print()
    
    # Projection Big Data
    print("🎯 PROJECTION POUR BIG DATA")
    print("-"*70)
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM traffic_data 
        WHERE timestamp > NOW() - INTERVAL '1 hour'
    """)
    hourly_rate = cursor.fetchone()[0]
    
    projections = {
        "1 jour": hourly_rate * 24,
        "1 semaine": hourly_rate * 24 * 7,
        "1 mois": hourly_rate * 24 * 30,
        "6 mois": hourly_rate * 24 * 180,
        "1 an": hourly_rate * 24 * 365
    }
    
    for period, records in projections.items():
        size_mb = (records * 500) / (1024 * 1024)  # Estimation 500 bytes/record
        print(f"  {period:12} : {records:>15,} records → ~{size_mb:>8,.0f} MB")
    
    print()
    
    # Recommandations
    print("💡 RECOMMANDATIONS POUR BIG DATA")
    print("-"*70)
    
    if total_records < 100000:
        print("  ⚠️  Volume actuel : FAIBLE (< 100K records)")
        print("  ➜  Recommandation : Générer des données historiques")
        print()
    elif total_records < 1000000:
        print("  ⚠️  Volume actuel : MOYEN (100K - 1M records)")
        print("  ➜  Recommandation : Augmenter la fréquence de génération")
        print()
    else:
        print("  ✅ Volume actuel : BON (> 1M records)")
        print()
    
    print("  Critères Big Data (règle des 3V) :")
    print("    • Volume  : > 1 million de records")
    print("    • Vélocité : > 1000 records/seconde")
    print("    • Variété : Multiple sources de données ✓")
    print()
    
    print("  Actions suggérées :")
    print("    1. Générer des données historiques (6-12 mois)")
    print("    2. Augmenter la fréquence (5s → 1s)")
    print("    3. Ajouter plus de capteurs (19 → 100+)")
    print("    4. Activer Spark streaming pour le traitement")
    print()
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        analyze_data_volume()
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print("\n💡 Assurez-vous que PostgreSQL est accessible sur localhost:5432")
