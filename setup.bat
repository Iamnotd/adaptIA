@echo off
title Instalacion de Orion - adaptIA
color 0A

echo ============================================
echo        INSTALADOR DE ORION - adaptIA
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Descarga Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python detectado.
echo.

echo Creando carpeta temporal sin espacios para Whisper...
if not exist "C:\adaptIA_temp" mkdir "C:\adaptIA_temp"
echo [OK] Carpeta C:\adaptIA_temp creada.
echo.

echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install python-dotenv loguru SpeechRecognition pyaudio pyttsx3 pyautogui pygetwindow psutil sqlalchemy requests groq openai-whisper pycaw comtypes

echo.
echo ============================================
echo   INSTALACION COMPLETADA
echo ============================================
echo.
echo Proximos pasos:
echo 1. Abre el archivo .env y pega tu Groq API key
echo 2. Ejecuta start.bat para iniciar Orion
echo.
pause
