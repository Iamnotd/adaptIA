@echo off
title Orion - adaptIA
color 0B

echo Iniciando Orion - adaptIA...
echo.

if not exist "C:\adaptIA_temp" mkdir "C:\adaptIA_temp"

python main.py

pause
