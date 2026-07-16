@echo off
cd /d "%~dp0"
title Instalacion de Orion - adaptIA
color 0A

echo ============================================
echo        INSTALADOR DE ORION - adaptIA
echo ============================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python no esta instalado o no esta agregado al PATH.
  echo Instala Python 3.11 de 64 bits y marca Add Python to PATH.
  pause
  exit /b 1
)

for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYVER=%%V
echo [OK] Python %PYVER% detectado.
echo Recomendado para este proyecto: Python 3.11 de 64 bits.
if not exist "C:\adaptIA_temp" mkdir "C:\adaptIA_temp"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [ERROR] Algunas dependencias no se instalaron.
  echo Si fallo PyAudio, usa Python 3.11 de 64 bits y vuelve a ejecutar este instalador.
  pause
  exit /b 1
)

echo.
echo [OK] Instalacion completada.
echo Ejecuta diagnostico.bat y luego start.bat.
pause
