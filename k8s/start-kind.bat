@echo off
echo ================================================
echo Creation cluster Kind pour Smart City Platform
echo ================================================
echo.

echo Verification de Kind...
kind version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Kind n'est pas installe
    echo Installation: choco install kind
    pause
    exit /b 1
)

echo Suppression de l'ancien cluster (si existe)...
kind delete cluster --name smart-city 2>nul

echo.
echo Creation du nouveau cluster avec config...
kind create cluster --config kind-config.yaml

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: Le cluster n'a pas pu etre cree
    pause
    exit /b 1
)

echo.
echo ================================================
echo Cluster Kind cree avec succes !
echo ================================================
echo.

echo Configuration kubectl...
kubectl config use-context kind-smart-city

echo.
echo Installation NGINX Ingress Controller...
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/kind/deploy.yaml

echo.
echo Attente que Ingress soit pret (30 secondes)...
timeout /t 30 /nobreak >nul

echo.
echo ================================================
echo Statut du cluster:
echo ================================================
kubectl cluster-info
kubectl get nodes

echo.
echo ================================================
echo Cluster pret ! Prochaines etapes :
echo   1. Charger les images Docker :
echo      kind load docker-image smart-city-api:latest
echo   2. Deployer la plateforme :
echo      kubectl apply -k .
echo ================================================
echo.
pause
