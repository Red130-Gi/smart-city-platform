@echo off
REM Smart City Platform - Kubernetes Deployment Script (Windows)
REM Usage: deploy.bat [action]
REM Example: deploy.bat deploy

set ACTION=%1
if "%ACTION%"=="" set ACTION=deploy

echo ================================================
echo Smart City Platform - Kubernetes Deployment
echo Action: %ACTION%
echo ================================================
echo.

if "%ACTION%"=="deploy" goto DEPLOY
if "%ACTION%"=="delete" goto DELETE
if "%ACTION%"=="status" goto STATUS
if "%ACTION%"=="logs" goto LOGS
goto UNKNOWN

:DEPLOY
echo Deploying Smart City Platform...
echo.

kubectl apply -k .

echo.
echo Waiting for pods to be ready...
timeout /t 10 /nobreak >nul

kubectl wait --for=condition=Available deployment/postgres -n smart-city --timeout=300s
kubectl wait --for=condition=Available deployment/mongodb -n smart-city --timeout=300s
kubectl wait --for=condition=Available deployment/redis -n smart-city --timeout=300s
kubectl wait --for=condition=Available deployment/kafka -n smart-city --timeout=300s
kubectl wait --for=condition=Available deployment/api -n smart-city --timeout=300s
kubectl wait --for=condition=Available deployment/grafana -n smart-city --timeout=300s

echo.
echo Pod Status:
kubectl get pods -n smart-city

echo.
echo ================================================
echo Deployment complete!
echo ================================================
echo.
echo Next steps:
echo   - API: kubectl port-forward svc/api 8000:8000 -n smart-city
echo   - Grafana: kubectl port-forward svc/grafana 3000:3000 -n smart-city
echo.
goto END

:DELETE
echo Deleting Smart City Platform...
kubectl delete -k .
echo Deletion complete!
goto END

:STATUS
echo Smart City Platform Status:
echo.
kubectl get all -n smart-city
goto END

:LOGS
set COMPONENT=%2
if "%COMPONENT%"=="" set COMPONENT=api
echo Logs for %COMPONENT%:
kubectl logs -f deployment/%COMPONENT% -n smart-city
goto END

:UNKNOWN
echo Unknown action: %ACTION%
echo Available actions: deploy, delete, status, logs
goto END

:END
pause
