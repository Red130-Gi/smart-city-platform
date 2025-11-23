#!/bin/bash

echo "================================================"
echo "Démarrage Minikube pour Smart City Platform"
echo "================================================"
echo ""

echo "Configuration:"
echo "  - CPUs: 4"
echo "  - Memory: 8GB"
echo "  - Disk: 20GB"
echo "  - Driver: Docker"
echo "  - Kubernetes: v1.28.0"
echo ""

echo "Démarrage de Minikube..."
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker --kubernetes-version=v1.28.0

if [ $? -ne 0 ]; then
    echo ""
    echo "ERREUR: Minikube n'a pas démarré correctement"
    echo ""
    echo "Vérifications:"
    echo "  1. Docker est-il démarré ?"
    echo "  2. Minikube est-il installé ? (brew install minikube)"
    echo "  3. Avez-vous assez de ressources disponibles ?"
    echo ""
    exit 1
fi

echo ""
echo "================================================"
echo "Minikube démarré avec succès !"
echo "================================================"
echo ""

echo "Activation des addons..."
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

echo ""
echo "Configuration kubectl..."
kubectl config use-context minikube

echo ""
echo "================================================"
echo "Statut du cluster:"
echo "================================================"
kubectl cluster-info

echo ""
echo "================================================"
echo "Cluster prêt ! Vous pouvez maintenant déployer :"
echo "  cd k8s"
echo "  kubectl apply -k ."
echo "================================================"
echo ""
