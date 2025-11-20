@echo off
echo.
echo ====================================================================
echo   GENERATION DE DONNEES HISTORIQUES BIG DATA
echo ====================================================================
echo.
echo Ce script va generer des mois de donnees historiques dans PostgreSQL
echo.
echo Options disponibles:
echo   1. LEGER    - 1 mois  (~500K records, ~30 min)
echo   2. MOYEN    - 3 mois  (~1.5M records, ~1.5h)
echo   3. COMPLET  - 6 mois  (~3M records, ~3h) - RECOMMANDE
echo   4. MASSIF   - 12 mois (~6M records, ~6h)
echo   5. ANNULER
echo.

set /p choice="Choisissez une option (1-5): "

if "%choice%"=="1" (
    set months=1
    set records=500,000
    set time=30 minutes
) else if "%choice%"=="2" (
    set months=3
    set records=1,500,000
    set time=1.5 heures
) else if "%choice%"=="3" (
    set months=6
    set records=3,000,000
    set time=3 heures
) else if "%choice%"=="4" (
    set months=12
    set records=6,000,000
    set time=6 heures
) else if "%choice%"=="5" (
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
echo Configuration selectionnee
echo ====================================================================
echo   Periode : %months% mois
echo   Records : ~%records%
echo   Duree estimee : ~%time%
echo ====================================================================
echo.
echo ATTENTION: Cette operation va generer beaucoup de donnees.
echo La base de donnees PostgreSQL va augmenter significativement.
echo.
set /p confirm="Confirmer? (O/N): "

if /i not "%confirm%"=="O" (
    echo.
    echo Operation annulee.
    exit /b 0
)

echo.
echo ====================================================================
echo GENERATION EN COURS...
echo ====================================================================
echo.
echo Veuillez patienter, cela peut prendre plusieurs heures...
echo.

REM Copier le script dans le conteneur
docker cp data-generation\generate_historical_data.py data-generator:/app/generate_historical_data.py

REM Créer un script Python qui répond automatiquement aux prompts
echo import os > %TEMP%\auto_generate.py
echo import sys >> %TEMP%\auto_generate.py
echo sys.path.insert(0, '/app') >> %TEMP%\auto_generate.py
echo. >> %TEMP%\auto_generate.py
echo # Mock input pour répondre automatiquement >> %TEMP%\auto_generate.py
echo original_input = input >> %TEMP%\auto_generate.py
echo def mock_input(prompt): >> %TEMP%\auto_generate.py
echo     if 'option' in prompt.lower(): >> %TEMP%\auto_generate.py
echo         return '%choice%' >> %TEMP%\auto_generate.py
echo     if 'continuer' in prompt.lower(): >> %TEMP%\auto_generate.py
echo         return 'y' >> %TEMP%\auto_generate.py
echo     return original_input(prompt) >> %TEMP%\auto_generate.py
echo. >> %TEMP%\auto_generate.py
echo __builtins__['input'] = mock_input >> %TEMP%\auto_generate.py
echo. >> %TEMP%\auto_generate.py
echo exec(open('/app/generate_historical_data.py').read()) >> %TEMP%\auto_generate.py

docker cp %TEMP%\auto_generate.py data-generator:/app/

REM Exécuter la génération
docker exec data-generator python /app/auto_generate.py

echo.
echo ====================================================================
echo GENERATION TERMINEE
echo ====================================================================
echo.
echo Verification du volume de donnees:
docker exec postgres psql -U smart_city -d smart_city_db -t -c "SELECT 'Traffic:', COUNT(*) FROM traffic_data UNION ALL SELECT 'Transport:', COUNT(*) FROM public_transport UNION ALL SELECT 'Parking:', COUNT(*) FROM parking_data"

echo.
echo ====================================================================
echo Pour analyser le volume complet, executez:
echo   python scripts\analyze_data_volume.py
echo ====================================================================
pause
