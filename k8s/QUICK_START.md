# 🚀 Quick Start - Déploiement Kubernetes Local

**3 méthodes simples pour tester la plateforme Smart City sur Kubernetes**

---

## ✅ Méthode 1 : Script Automatique (RECOMMANDÉ)

### Windows
```bash
# Démarrer Minikube
cd k8s
start-minikube.bat

# Déployer la plateforme
kubectl apply -k .

# Accéder aux services
kubectl port-forward svc/api 8000:8000 -n smart-city
kubectl port-forward svc/grafana 3000:3000 -n smart-city
```

### Linux/Mac
```bash
# Démarrer Minikube
cd k8s
chmod +x start-minikube.sh
./start-minikube.sh

# Déployer la plateforme
kubectl apply -k .

# Accéder aux services
kubectl port-forward svc/api 8000:8000 -n smart-city &
kubectl port-forward svc/grafana 3000:3000 -n smart-city &
```

---

## ✅ Méthode 2 : Commande Directe Minikube

```bash
# 1. Démarrer Minikube avec les bonnes options
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# 2. Activer les addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Déployer
cd k8s
kubectl apply -k .

# 4. Vérifier
kubectl get pods -n smart-city

# 5. Accéder aux services
kubectl port-forward svc/api 8000:8000 -n smart-city
kubectl port-forward svc/grafana 3000:3000 -n smart-city
```

---

## ✅ Méthode 3 : Kind (Alternative à Minikube)

```bash
# 1. Créer le cluster Kind
cd k8s
kind create cluster --config kind-config.yaml

# 2. Charger les images Docker (si images locales)
kind load docker-image smart-city-api:latest --name smart-city
kind load docker-image smart-city-spark-streaming:latest --name smart-city
kind load docker-image smart-city-data-generator:latest --name smart-city

# 3. Déployer
kubectl apply -k .

# 4. Services accessibles directement
# API: http://localhost:8000
# Grafana: http://localhost:3000
```

---

## 🔍 Vérification du Déploiement

```bash
# Voir tous les pods
kubectl get pods -n smart-city

# Attendre que tout soit prêt
kubectl wait --for=condition=Ready pods --all -n smart-city --timeout=300s

# Voir les services
kubectl get svc -n smart-city

# Logs en temps réel
kubectl logs -f deployment/api -n smart-city
kubectl logs -f deployment/spark-streaming -n smart-city
```

---

## 🌐 Accès aux Services

### Via Port-Forward

```bash
# API (dans un terminal)
kubectl port-forward svc/api 8000:8000 -n smart-city

# Grafana (dans un autre terminal)
kubectl port-forward svc/grafana 3000:3000 -n smart-city

# PostgreSQL (pour debug)
kubectl port-forward svc/postgres 5432:5432 -n smart-city

# MongoDB (pour debug)
kubectl port-forward svc/mongodb 27017:27017 -n smart-city
```

**URLs :**
- API : http://localhost:8000
- API Docs : http://localhost:8000/docs
- Grafana : http://localhost:3000 (admin / smartcity123)

---

## 🛠️ Commandes Utiles

### Gestion du Cluster

```bash
# Status Minikube
minikube status

# Dashboard Kubernetes
minikube dashboard

# Arrêter Minikube
minikube stop

# Supprimer Minikube
minikube delete

# SSH dans Minikube
minikube ssh
```

### Gestion des Pods

```bash
# Lister les pods
kubectl get pods -n smart-city

# Détails d'un pod
kubectl describe pod <pod-name> -n smart-city

# Logs d'un pod
kubectl logs <pod-name> -n smart-city

# Logs temps réel
kubectl logs -f <pod-name> -n smart-city

# Shell dans un pod
kubectl exec -it <pod-name> -n smart-city -- /bin/bash
```

### Scalabilité

```bash
# Scaler l'API
kubectl scale deployment api --replicas=3 -n smart-city

# Vérifier
kubectl get pods -n smart-city | grep api
```

---

## 🧹 Nettoyage

```bash
# Supprimer la plateforme
kubectl delete -k k8s/

# Ou supprimer le namespace complet
kubectl delete namespace smart-city

# Arrêter Minikube
minikube stop

# Supprimer complètement Minikube
minikube delete
```

---

## ⚠️ Troubleshooting

### Erreur : "Insufficient memory"
```bash
# Augmenter la mémoire de Minikube
minikube delete
minikube start --cpus=4 --memory=10240 --disk-size=20g
```

### Erreur : "ImagePullBackOff"
```bash
# Vérifier l'image
kubectl describe pod <pod-name> -n smart-city

# Pour tests locaux, utiliser imagePullPolicy: IfNotPresent
# Éditer le deployment :
kubectl edit deployment api -n smart-city
# Changer imagePullPolicy: Always -> IfNotPresent
```

### Erreur : "Pods not ready"
```bash
# Voir les logs
kubectl logs <pod-name> -n smart-city

# Voir les événements
kubectl get events -n smart-city --sort-by='.lastTimestamp'

# Vérifier les ressources
kubectl top nodes
kubectl top pods -n smart-city
```

### Docker Desktop non démarré
```bash
# Windows : Démarrer Docker Desktop
# Vérifier avec :
docker ps

# Puis redémarrer Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g
```

---

## 📊 Commande Complète (Copier-Coller)

### Windows - Tout en Une Commande

```powershell
# Démarrer Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker; `
minikube addons enable ingress; `
minikube addons enable metrics-server; `
cd k8s; `
kubectl apply -k .; `
Start-Sleep -Seconds 30; `
kubectl get pods -n smart-city; `
Write-Host "`nAPI: kubectl port-forward svc/api 8000:8000 -n smart-city"; `
Write-Host "Grafana: kubectl port-forward svc/grafana 3000:3000 -n smart-city"
```

### Linux/Mac - Tout en Une Commande

```bash
# Démarrer Minikube
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker && \
minikube addons enable ingress && \
minikube addons enable metrics-server && \
cd k8s && \
kubectl apply -k . && \
sleep 30 && \
kubectl get pods -n smart-city && \
echo "\nAPI: kubectl port-forward svc/api 8000:8000 -n smart-city" && \
echo "Grafana: kubectl port-forward svc/grafana 3000:3000 -n smart-city"
```

---

## ✅ Checklist de Démarrage

- [ ] Docker Desktop démarré
- [ ] Minikube installé (`choco install minikube` ou `brew install minikube`)
- [ ] kubectl installé (`choco install kubernetes-cli`)
- [ ] Au moins 8GB RAM disponible
- [ ] Au moins 20GB disque disponible
- [ ] Cluster Minikube démarré
- [ ] Addons activés (ingress, metrics-server)
- [ ] Plateforme déployée (`kubectl apply -k k8s/`)
- [ ] Pods en état Running
- [ ] Port-forward configuré
- [ ] Services accessibles

---

**Démarrage rapide réussi ! 🚀**
