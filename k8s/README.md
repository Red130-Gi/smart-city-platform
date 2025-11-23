# 🚀 Déploiement Kubernetes - Smart City Platform

Ce dossier contient tous les manifests Kubernetes pour déployer la plateforme Smart City sur un cluster Kubernetes.

---

## 📁 Structure des Manifests

```
k8s/
├── namespace.yaml                  # Namespace smart-city
├── kustomization.yaml             # Kustomize configuration
├── ingress.yaml                   # Ingress pour accès externe
├── secrets/                       # Credentials
│   ├── database-secrets.yaml
│   └── kafka-secrets.yaml
├── configmaps/                    # Configuration
│   └── app-config.yaml
├── storage/                       # PersistentVolumeClaims
│   ├── postgres-pvc.yaml
│   ├── mongodb-pvc.yaml
│   ├── kafka-pvc.yaml
│   └── grafana-pvc.yaml
├── deployments/                   # Déploiements d'applications
│   ├── postgres-deployment.yaml
│   ├── mongodb-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── zookeeper-deployment.yaml
│   ├── kafka-deployment.yaml
│   ├── api-deployment.yaml
│   ├── grafana-deployment.yaml
│   ├── spark-streaming-deployment.yaml
│   └── data-generator-deployment.yaml
└── services/                      # Services Kubernetes
    ├── postgres-service.yaml
    ├── mongodb-service.yaml
    ├── redis-service.yaml
    ├── zookeeper-service.yaml
    ├── kafka-service.yaml
    ├── api-service.yaml
    └── grafana-service.yaml
```

---

## 🔧 Prérequis

### 1. Cluster Kubernetes
```bash
# Vérifier kubectl
kubectl version --client

# Vérifier le cluster
kubectl cluster-info
```

**Options de cluster :**
- **Minikube** (local) : `minikube start --memory=8192 --cpus=4`
- **Kind** (local) : `kind create cluster --config kind-config.yaml`
- **EKS** (AWS) : Cluster managed
- **GKE** (Google Cloud) : Cluster managed
- **AKS** (Azure) : Cluster managed

### 2. Outils Requis
```bash
# Installer kubectl
choco install kubernetes-cli

# Installer kustomize (optionnel)
choco install kustomize

# Installer Helm (pour Ingress Controller)
choco install kubernetes-helm
```

### 3. Images Docker
Les images Docker doivent être construites et poussées vers un registry accessible par Kubernetes :

```bash
# Build images
docker build -t <registry>/smart-city-api:latest ./api
docker build -t <registry>/smart-city-spark-streaming:latest ./data-pipeline
docker build -t <registry>/smart-city-data-generator:latest ./data-generation

# Push vers registry
docker push <registry>/smart-city-api:latest
docker push <registry>/smart-city-spark-streaming:latest
docker push <registry>/smart-city-data-generator:latest
```

**Note :** Pour Minikube/Kind local, utilisez `imagePullPolicy: IfNotPresent` et chargez les images localement :
```bash
# Minikube
eval $(minikube docker-env)
docker build -t smart-city-api:latest ./api

# Kind
kind load docker-image smart-city-api:latest
```

---

## 🚀 Déploiement

### Option 1 : Déploiement avec Kustomize (Recommandé)

```bash
# Déployer tout
kubectl apply -k k8s/

# Vérifier le déploiement
kubectl get all -n smart-city

# Voir les logs
kubectl logs -f deployment/api -n smart-city
```

### Option 2 : Déploiement Manuel (Étape par Étape)

```bash
# 1. Créer le namespace
kubectl apply -f k8s/namespace.yaml

# 2. Créer le stockage
kubectl apply -f k8s/storage/

# 3. Créer les secrets et configmaps
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/configmaps/

# 4. Déployer les bases de données
kubectl apply -f k8s/deployments/postgres-deployment.yaml
kubectl apply -f k8s/deployments/mongodb-deployment.yaml
kubectl apply -f k8s/deployments/redis-deployment.yaml

# 5. Déployer Kafka
kubectl apply -f k8s/deployments/zookeeper-deployment.yaml
kubectl apply -f k8s/deployments/kafka-deployment.yaml

# 6. Créer les services
kubectl apply -f k8s/services/

# 7. Déployer les applications
kubectl apply -f k8s/deployments/api-deployment.yaml
kubectl apply -f k8s/deployments/grafana-deployment.yaml
kubectl apply -f k8s/deployments/spark-streaming-deployment.yaml
kubectl apply -f k8s/deployments/data-generator-deployment.yaml

# 8. Configurer l'Ingress
kubectl apply -f k8s/ingress.yaml
```

---

## 📊 Vérification du Déploiement

### Vérifier les Pods
```bash
# Tous les pods
kubectl get pods -n smart-city

# Attendre que tous soient Running
kubectl wait --for=condition=Ready pods --all -n smart-city --timeout=300s
```

### Vérifier les Services
```bash
kubectl get svc -n smart-city
```

### Vérifier les PVC
```bash
kubectl get pvc -n smart-city
```

### Logs en Temps Réel
```bash
# API
kubectl logs -f deployment/api -n smart-city

# Spark Streaming
kubectl logs -f deployment/spark-streaming -n smart-city

# Générateur de données
kubectl logs -f deployment/data-generator -n smart-city
```

---

## 🌐 Accès aux Services

### Via LoadBalancer (Cloud)
```bash
# Obtenir l'IP externe de l'API
kubectl get svc api -n smart-city

# Obtenir l'IP externe de Grafana
kubectl get svc grafana -n smart-city
```

### Via Port-Forwarding (Local)
```bash
# API
kubectl port-forward svc/api 8000:8000 -n smart-city
# Accès: http://localhost:8000

# Grafana
kubectl port-forward svc/grafana 3000:3000 -n smart-city
# Accès: http://localhost:3000
# Login: admin / smartcity123

# PostgreSQL (pour debug)
kubectl port-forward svc/postgres 5432:5432 -n smart-city

# MongoDB (pour debug)
kubectl port-forward svc/mongodb 27017:27017 -n smart-city
```

### Via Ingress (avec Ingress Controller)
```bash
# Installer NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Ajouter dans /etc/hosts (ou C:\Windows\System32\drivers\etc\hosts sur Windows)
<INGRESS_IP> api.smartcity.local
<INGRESS_IP> grafana.smartcity.local

# Accès:
# - API: http://api.smartcity.local
# - Grafana: http://grafana.smartcity.local
```

---

## 🔍 Monitoring et Debug

### Dashboard Kubernetes
```bash
# Déployer le dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Créer un token
kubectl -n kubernetes-dashboard create token admin-user

# Port forward
kubectl proxy

# Accès: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### Métriques de Ressources
```bash
# Top pods
kubectl top pods -n smart-city

# Top nodes
kubectl top nodes

# Describe un pod
kubectl describe pod <pod-name> -n smart-city

# Events
kubectl get events -n smart-city --sort-by='.lastTimestamp'
```

### Shell dans un Pod
```bash
# PostgreSQL
kubectl exec -it deployment/postgres -n smart-city -- psql -U smart_city -d smart_city_db

# MongoDB
kubectl exec -it deployment/mongodb -n smart-city -- mongosh -u admin -p smartcity123

# API
kubectl exec -it deployment/api -n smart-city -- /bin/bash
```

---

## 📈 Scalabilité

### Scaler les Déploiements
```bash
# Scaler l'API (2 → 5 replicas)
kubectl scale deployment api --replicas=5 -n smart-city

# Scaler Spark Streaming
kubectl scale deployment spark-streaming --replicas=2 -n smart-city

# Auto-scaling (HPA)
kubectl autoscale deployment api --cpu-percent=70 --min=2 --max=10 -n smart-city
```

### Vérifier l'Autoscaling
```bash
kubectl get hpa -n smart-city
```

---

## 🔄 Mise à Jour

### Rolling Update
```bash
# Mettre à jour l'image de l'API
kubectl set image deployment/api api=smart-city-api:v2.0 -n smart-city

# Suivre le rollout
kubectl rollout status deployment/api -n smart-city

# Historique
kubectl rollout history deployment/api -n smart-city

# Rollback si nécessaire
kubectl rollout undo deployment/api -n smart-city
```

---

## 🧹 Nettoyage

### Supprimer Tout
```bash
# Via kustomize
kubectl delete -k k8s/

# Ou manuellement
kubectl delete namespace smart-city

# Vérifier
kubectl get all -n smart-city
```

### Supprimer un Composant Spécifique
```bash
kubectl delete deployment api -n smart-city
kubectl delete svc api -n smart-city
```

---

## 🔐 Sécurité

### Secrets
Les secrets sont stockés dans `k8s/secrets/`. **NE PAS COMMITER les secrets en production !**

Pour la production, utilisez :
- **Sealed Secrets** : `kubeseal`
- **External Secrets Operator** : Intégration avec Azure Key Vault, AWS Secrets Manager, etc.
- **Vault** : HashiCorp Vault

### RBAC (Role-Based Access Control)
```yaml
# Exemple: Créer un ServiceAccount avec accès limité
apiVersion: v1
kind: ServiceAccount
metadata:
  name: smart-city-reader
  namespace: smart-city
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: smart-city
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]
```

---

## 📝 Configuration Avancée

### Ressources Limits/Requests
Les limites sont configurées dans chaque deployment. Ajustez selon vos besoins :

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Health Checks
- **livenessProbe** : Redémarre le pod si l'application est bloquée
- **readinessProbe** : Retire le pod du load balancer si non prêt

### Persistence
Les PVC utilisent la `storageClassName: standard`. Modifiez selon votre cluster :
- **AWS EBS** : `gp2`, `gp3`
- **GCE PD** : `pd-standard`, `pd-ssd`
- **Azure Disk** : `managed-premium`
- **Local** : `local-path` (Minikube/Kind)

---

## 🎯 Best Practices

1. **Namespaces** : Isoler les environnements (dev, staging, prod)
2. **Labels** : Utiliser des labels cohérents pour filtrer
3. **Resource Limits** : Toujours définir requests/limits
4. **Health Checks** : Configurer liveness/readiness probes
5. **Secrets** : Ne jamais commiter en clair
6. **Monitoring** : Déployer Prometheus + Grafana
7. **Logging** : Utiliser FluentD/Fluentbit + Elasticsearch
8. **Backup** : Sauvegarder les PVC régulièrement

---

## 📞 Support

Pour plus d'informations :
- Documentation Kubernetes : https://kubernetes.io/docs/
- Kubectl Cheat Sheet : https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Kustomize : https://kustomize.io/

---

**Déploiement Kubernetes Smart City Platform - Prêt pour Production ! 🚀**
