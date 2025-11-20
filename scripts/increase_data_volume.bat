@echo off
echo.
echo ====================================================================
echo   AUGMENTATION DU VOLUME DE DONNEES - SMART CITY BIG DATA
echo ====================================================================
echo.
echo Ce script va modifier la configuration pour generer plus de donnees.
echo.
echo Options disponibles:
echo   1. LEGER    - Intervalle 3s (x1.7 volume)
echo   2. MOYEN    - Intervalle 2s (x2.5 volume)
echo   3. INTENSIF - Intervalle 1s (x5 volume) - RECOMMANDE pour Big Data
echo   4. ANNULER
echo.

set /p choice="Choisissez une option (1-4): "

if "%choice%"=="1" (
    set interval=3
    set mode=LEGER
) else if "%choice%"=="2" (
    set interval=2
    set mode=MOYEN
) else if "%choice%"=="3" (
    set interval=1
    set mode=INTENSIF
) else if "%choice%"=="4" (
    echo.
    echo Operation annulee.
    exit /b 0
) else (
    echo.
    echo Choix invalide.
    exit /b 1
)

echo.
echo ====================================================================
echo Configuration selectionnee: %mode%
echo Intervalle de generation: %interval% seconde(s)
echo ====================================================================
echo.
echo ATTENTION: Cette modification va:
echo   - Arreter le data-generator
echo   - Modifier la configuration
echo   - Redemarrer avec le nouvel intervalle
echo.
set /p confirm="Confirmer? (O/N): "

if /i not "%confirm%"=="O" (
    echo.
    echo Operation annulee.
    exit /b 0
)

echo.
echo Arret du data-generator...
docker-compose stop data-generator

echo.
echo Modification de docker-compose.yml...
powershell -Command "(Get-Content docker-compose.yml) -replace 'GENERATION_INTERVAL=[0-9]+', 'GENERATION_INTERVAL=%interval%' | Set-Content docker-compose.yml"

echo.
echo Redemarrage du data-generator...
docker-compose up -d data-generator

echo.
echo ====================================================================
echo CONFIGURATION MODIFIEE AVEC SUCCES
echo ====================================================================
echo.
echo Nouveau parametre: GENERATION_INTERVAL=%interval%
echo.
echo Verification du fonctionnement:
echo   docker-compose logs -f data-generator
echo.
echo Volume attendu:
if "%interval%"=="1" (
    echo   - ~560,000 records/jour
    echo   - ~17 millions records/mois
    echo   - ~100 millions records/6 mois
)
if "%interval%"=="2" (
    echo   - ~280,000 records/jour
    echo   - ~8.5 millions records/mois
    echo   - ~50 millions records/6 mois
)
if "%interval%"=="3" (
    echo   - ~187,000 records/jour
    echo   - ~5.6 millions records/mois
    echo   - ~34 millions records/6 mois
)
echo.
echo ====================================================================
pause
