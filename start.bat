@echo off
cd /d "%~dp0"
title Orion - adaptIA
color 0B

echo Iniciando Orion - adaptIA...
echo No cierres esta ventana: aqui se mostraran los errores.
echo.

if not exist "C:\adaptIA_temp" mkdir "C:\adaptIA_temp"
python main.py

echo.
echo Orion se detuvo. Revisa el mensaje de error mostrado arriba.
pause
