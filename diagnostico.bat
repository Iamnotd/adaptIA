@echo off
cd /d "%~dp0"
title Diagnostico Orion
color 0E
echo ========================================
echo       DIAGNOSTICO DE ORION adaptIA
echo ========================================
echo.
python --version
if errorlevel 1 goto :python_error
echo.
echo [1] Comprobando dependencias principales...
python -c "import speech_recognition, pyaudio, pyttsx3, whisper, requests; print('[OK] Dependencias principales')"
if errorlevel 1 goto :deps_error
echo.
echo [2] Microfonos detectados:
python -c "import speech_recognition as sr; [print('  ['+str(i)+'] '+n) for i,n in enumerate(sr.Microphone.list_microphone_names())]"
echo.
echo [3] Probando apertura del microfono predeterminado...
python -c "import speech_recognition as sr; m=sr.Microphone(); print('[OK] Microfono abierto:', m.device_index)"
if errorlevel 1 goto :mic_error
echo.
echo Diagnostico basico completado. Ejecuta start.bat.
pause
exit /b 0
:python_error
echo [ERROR] Python no esta instalado o no esta en PATH.
pause
exit /b 1
:deps_error
echo [ERROR] Faltan dependencias. Ejecuta setup.bat.
pause
exit /b 1
:mic_error
echo [ERROR] Windows/PyAudio no permiten abrir el microfono.
echo Activa: Configuracion ^> Privacidad ^> Microfono ^> permitir aplicaciones de escritorio.
pause
exit /b 1
