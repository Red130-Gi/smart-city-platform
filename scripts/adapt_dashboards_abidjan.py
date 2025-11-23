"""
Script pour adapter tous les dashboards Grafana pour Abidjan
- Change les titres pour inclure "Abidjan"
- Met à jour les coordonnées GPS du centre (5.3364°N, -4.0267°W)
- Adapte les descriptions et textes
"""

import json
import os
import re
from pathlib import Path

# Configuration Abidjan
ABIDJAN_CENTER = {
    'lat': 5.3364,
    'lon': -4.0267
}

ABIDJAN_ZONES = ['zone-centre', 'zone-nord', 'zone-est', 'zone-sud', 'zone-ouest']

# Chemins des dashboards
DASHBOARD_PATHS = [
    'grafana/provisioning/dashboards/json/',
    'grafana/dashboards/json/'
]

def update_title_with_abidjan(title):
    """Ajoute 'Abidjan' au titre s'il n'y est pas déjà"""
    if 'Abidjan' not in title:
        # Remplacer "Smart City" par "Smart City Abidjan"
        if 'Smart City' in title:
            return title.replace('Smart City', 'Smart City Abidjan')
        # Sinon ajouter "- Abidjan" à la fin
        return f"{title} - Abidjan"
    return title

def update_description_with_abidjan(description):
    """Met à jour la description pour mentionner Abidjan"""
    if description and 'Abidjan' not in description:
        abidjan_info = "Ville: Abidjan, Côte d'Ivoire (5M habitants). "
        return abidjan_info + description
    return description

def update_geomap_center(panel):
    """Met à jour le centre de la carte GeoMap pour Abidjan"""
    if panel.get('type') == 'geomap':
        # Chercher dans options.view
        if 'options' in panel and 'view' in panel['options']:
            panel['options']['view']['lat'] = ABIDJAN_CENTER['lat']
            panel['options']['view']['lon'] = ABIDJAN_CENTER['lon']
            # Zoom adapté pour voir toute la ville
            if 'zoom' in panel['options']['view']:
                panel['options']['view']['zoom'] = 11
        
        # Chercher dans fieldConfig pour des coordonnées par défaut
        if 'fieldConfig' in panel:
            if 'defaults' in panel['fieldConfig']:
                defaults = panel['fieldConfig']['defaults']
                if 'custom' in defaults and 'center' in defaults['custom']:
                    defaults['custom']['center'] = {
                        'lat': ABIDJAN_CENTER['lat'],
                        'lon': ABIDJAN_CENTER['lon']
                    }
    
    return panel

def update_text_panels(panel):
    """Met à jour les panels de texte avec des infos Abidjan"""
    if panel.get('type') in ['text', 'stat']:
        if 'options' in panel and 'content' in panel['options']:
            content = panel['options']['content']
            
            # Remplacer références génériques par Abidjan
            replacements = {
                'ville': 'Abidjan',
                'city': 'Abidjan',
                'Smart City': 'Smart City Abidjan',
                'la ville': 'Abidjan',
                'notre ville': 'Abidjan',
            }
            
            for old, new in replacements.items():
                if old in content and 'Abidjan' not in content:
                    content = content.replace(old, new, 1)
            
            panel['options']['content'] = content
    
    return panel

def add_abidjan_tags(tags):
    """Ajoute des tags spécifiques à Abidjan"""
    if tags is None:
        tags = []
    
    abidjan_tags = ['abidjan', 'cote-ivoire', 'africa']
    for tag in abidjan_tags:
        if tag not in tags:
            tags.append(tag)
    
    return tags

def process_dashboard(filepath):
    """Traite un dashboard pour l'adapter à Abidjan"""
    print(f"\n📊 Traitement: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            dashboard = json.load(f)
        
        # Backup original
        backup_path = filepath.replace('.json', '.json.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2)
        
        # Mettre à jour le titre
        if 'title' in dashboard:
            old_title = dashboard['title']
            dashboard['title'] = update_title_with_abidjan(dashboard['title'])
            if old_title != dashboard['title']:
                print(f"  ✓ Titre: {old_title} → {dashboard['title']}")
        
        # Mettre à jour la description
        if 'description' in dashboard:
            dashboard['description'] = update_description_with_abidjan(dashboard['description'])
        
        # Ajouter tags Abidjan
        if 'tags' in dashboard:
            old_tags = dashboard['tags'].copy() if dashboard['tags'] else []
            dashboard['tags'] = add_abidjan_tags(dashboard['tags'])
            new_tags = [tag for tag in dashboard['tags'] if tag not in old_tags]
            if new_tags:
                print(f"  ✓ Tags ajoutés: {', '.join(new_tags)}")
        
        # Traiter les panels
        if 'panels' in dashboard:
            for panel in dashboard['panels']:
                # Mettre à jour titre du panel
                if 'title' in panel:
                    old_panel_title = panel['title']
                    panel['title'] = update_title_with_abidjan(panel['title'])
                
                # Mettre à jour GeoMap
                panel = update_geomap_center(panel)
                
                # Mettre à jour panels de texte
                panel = update_text_panels(panel)
                
                # Traiter les sous-panels (rows)
                if 'panels' in panel:
                    for subpanel in panel['panels']:
                        if 'title' in subpanel:
                            subpanel['title'] = update_title_with_abidjan(subpanel['title'])
                        subpanel = update_geomap_center(subpanel)
                        subpanel = update_text_panels(subpanel)
        
        # Ajouter annotation Abidjan
        if 'annotations' not in dashboard:
            dashboard['annotations'] = {'list': []}
        
        # Sauvegarder le dashboard modifié
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Dashboard adapté pour Abidjan!")
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def main():
    """Traite tous les dashboards"""
    print("="*70)
    print("ADAPTATION DASHBOARDS GRAFANA POUR ABIDJAN")
    print("="*70)
    print(f"\n🌍 Coordonnées Abidjan: {ABIDJAN_CENTER['lat']}°N, {ABIDJAN_CENTER['lon']}°W")
    print(f"📊 Zones: {', '.join(ABIDJAN_ZONES)}\n")
    
    base_dir = Path(__file__).parent.parent
    dashboards_processed = 0
    dashboards_success = 0
    
    # Traiter tous les dashboards
    for dashboard_path in DASHBOARD_PATHS:
        full_path = base_dir / dashboard_path
        if not full_path.exists():
            continue
        
        for json_file in full_path.glob('*.json'):
            if '.backup' not in str(json_file):
                dashboards_processed += 1
                if process_dashboard(str(json_file)):
                    dashboards_success += 1
    
    print("\n" + "="*70)
    print(f"✅ TERMINÉ: {dashboards_success}/{dashboards_processed} dashboards adaptés")
    print("="*70)
    print("\nBackups créés avec extension .json.backup")
    print("\nRedémarrez Grafana pour appliquer les changements:")
    print("  docker-compose restart grafana")
    print("\nAccès: http://localhost:3000")
    print("Login: admin / smartcity123")

if __name__ == '__main__':
    main()
