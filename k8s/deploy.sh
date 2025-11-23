#!/bin/bash

# Smart City Platform - Kubernetes Deployment Script
# Usage: ./deploy.sh [env] [action]
# Example: ./deploy.sh local deploy

set -e

ENV=${1:-local}
ACTION=${2:-deploy}

echo "================================================"
echo "Smart City Platform - Kubernetes Deployment"
echo "Environment: $ENV"
echo "Action: $ACTION"
echo "================================================"
echo ""

# Function to wait for deployment
wait_for_deployment() {
    local deployment=$1
    echo "⏳ Waiting for $deployment to be ready..."
    kubectl wait --for=condition=Available deployment/$deployment -n smart-city --timeout=300s
    echo "✓ $deployment is ready"
}

# Function to check pod status
check_pods() {
    echo ""
    echo "📊 Pod Status:"
    kubectl get pods -n smart-city
}

case $ACTION in
    deploy)
        echo "🚀 Deploying Smart City Platform..."
        echo ""
        
        # Apply with kustomize
        kubectl apply -k .
        
        echo ""
        echo "⏳ Waiting for all pods to be ready..."
        sleep 10
        
        # Wait for critical services
        wait_for_deployment postgres
        wait_for_deployment mongodb
        wait_for_deployment redis
        wait_for_deployment zookeeper
        wait_for_deployment kafka
        wait_for_deployment api
        wait_for_deployment grafana
        
        check_pods
        
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "📌 Next steps:"
        echo "  - API: kubectl port-forward svc/api 8000:8000 -n smart-city"
        echo "  - Grafana: kubectl port-forward svc/grafana 3000:3000 -n smart-city"
        ;;
    
    delete)
        echo "🗑️  Deleting Smart City Platform..."
        kubectl delete -k .
        echo "✅ Deletion complete!"
        ;;
    
    status)
        echo "📊 Smart City Platform Status:"
        echo ""
        kubectl get all -n smart-city
        ;;
    
    logs)
        COMPONENT=${3:-api}
        echo "📜 Logs for $COMPONENT:"
        kubectl logs -f deployment/$COMPONENT -n smart-city
        ;;
    
    shell)
        COMPONENT=${3:-api}
        echo "🐚 Opening shell in $COMPONENT..."
        kubectl exec -it deployment/$COMPONENT -n smart-city -- /bin/bash
        ;;
    
    *)
        echo "❌ Unknown action: $ACTION"
        echo "Available actions: deploy, delete, status, logs, shell"
        exit 1
        ;;
esac
