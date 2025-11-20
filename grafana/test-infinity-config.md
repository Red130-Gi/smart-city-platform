# Configuration Manuelle de la Datasource Infinity

## Étapes pour Configurer Infinity dans Grafana

### 1. Accéder aux Settings de la Datasource

1. Ouvrir Grafana : http://localhost:3000
2. Aller dans **Configuration** (⚙️) → **Data sources**
3. Chercher **"Infinity"** dans la liste
4. Cliquer sur **"Infinity"**

### 2. Configuration des Allowed Hosts

Dans la page de configuration :

1. **Section "Security"** ou **"Allowed Hosts"**
   - Ajouter ces URLs (une par ligne) :
   ```
   http://api:8000
   http://smart-city-api:8000
   http://localhost:8000
   http://127.0.0.1:8000
   ```

2. **Section "Authentication"**
   - Method: `No Auth`
   - Forward OAuth Identity: `Off`

3. **Section "HTTP"**
   - Access: `Server (default)`
   - Whitelist cookies: Laisser vide

4. **Headers** (optionnel)
   - Header 1:
     - Name: `Content-Type`
     - Value: `application/json`

5. Cliquer **"Save & Test"**

### 3. Test de Configuration

#### Test Direct dans Infinity

1. Dans la datasource Infinity, aller dans l'onglet **"Query Inspector"**
2. Configuration de test :
   ```
   URL: http://api:8000/api/v1/stats
   Method: GET
   Parser: Backend
   Format: JSON
   ```
3. Cliquer **"Run Query"**

#### URLs de Test Disponibles

```
http://api:8000/health
http://api:8000/api/v1/stats
http://api:8000/api/v1/traffic/current
http://api:8000/api/v1/predict/traffic/future?zone_id=zone-1&horizon_hours=1
```

### 4. Si la Configuration Manuelle Échoue

#### Option A : Utiliser cURL depuis Grafana

```bash
# Test depuis le conteneur Grafana
docker exec -it grafana sh
wget -qO- http://api:8000/health
```

#### Option B : Modifier le Dashboard

Remplacer `http://api:8000` par `http://host.docker.internal:8000` dans les requêtes.

### 5. Alternative : Utiliser JSON Datasource

Si Infinity ne fonctionne pas, installer le **JSON API Datasource** :

```bash
docker-compose exec grafana grafana-cli plugins install marcusolsson-json-datasource
docker-compose restart grafana
```

Configuration JSON Datasource :
- URL: `http://api:8000`
- Access: `Server (default)`
- Custom HTTP Headers:
  - Header: `Content-Type`
  - Value: `application/json`
