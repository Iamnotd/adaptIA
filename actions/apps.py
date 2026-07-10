"""
actions/apps.py
Acciones para abrir, cerrar y gestionar aplicaciones en Windows.
"""

import os
import subprocess
import psutil
from modules.logger import get_logger

logger = get_logger()

# Mapa de nombres comunes en español/inglés a comandos ejecutables de Windows.
# Se puede ampliar según las apps que el usuario use más.
APPS_CONOCIDAS = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "navegador": "chrome.exe",
    "edge": "msedge.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "bloc de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "explorador de archivos": "explorer.exe",
    "spotify": "spotify.exe",
    "whatsapp": "WhatsApp.exe",
    "vscode": "Code.exe",
    "visual studio code": "Code.exe",
    "discord": "Discord.exe",
    "outlook": "outlook.exe",
}


def abrir_app(nombre_app):
    """
    Abre una aplicación de Windows por nombre.
    Primero busca en el mapa de apps conocidas; si no la encuentra,
    intenta ejecutarla directamente asumiendo que está en el PATH del sistema.
    """
    nombre_normalizado = nombre_app.lower().strip()
    ejecutable = APPS_CONOCIDAS.get(nombre_normalizado, nombre_app)

    try:
        os.startfile(ejecutable)
        logger.info(f"Aplicación abierta: {ejecutable}")
        return True, f"He abierto {nombre_app}."
    except FileNotFoundError:
        try:
            subprocess.Popen(ejecutable, shell=True)
            logger.info(f"Aplicación abierta vía subprocess: {ejecutable}")
            return True, f"He abierto {nombre_app}."
        except Exception as e:
            logger.error(f"No se pudo abrir la aplicación '{nombre_app}': {e}")
            return False, f"No pude encontrar o abrir {nombre_app}."
    except Exception as e:
        logger.error(f"Error abriendo aplicación '{nombre_app}': {e}")
        return False, f"Ocurrió un error al intentar abrir {nombre_app}."


def cerrar_app(nombre_app):
    """
    Cierra una aplicación buscando su proceso por nombre entre los procesos activos.
    """
    nombre_normalizado = nombre_app.lower().strip()
    ejecutable = APPS_CONOCIDAS.get(nombre_normalizado, nombre_app)
    ejecutable_base = ejecutable.replace(".exe", "").lower()

    cerrado = False
    try:
        for proceso in psutil.process_iter(["pid", "name"]):
            nombre_proceso = (proceso.info["name"] or "").lower()
            if ejecutable_base in nombre_proceso:
                proceso.terminate()
                cerrado = True
                logger.info(f"Proceso terminado: {nombre_proceso} (PID {proceso.info['pid']})")

        if cerrado:
            return True, f"He cerrado {nombre_app}."
        else:
            return False, f"No encontré {nombre_app} abierto en este momento."
    except Exception as e:
        logger.error(f"Error cerrando aplicación '{nombre_app}': {e}")
        return False, f"Ocurrió un error al intentar cerrar {nombre_app}."


def listar_apps_abiertas():
    """Devuelve una lista de nombres de procesos visibles actualmente en ejecución."""
    try:
        nombres = set()
        for proceso in psutil.process_iter(["name"]):
            if proceso.info["name"]:
                nombres.add(proceso.info["name"])
        return True, list(nombres)
    except Exception as e:
        logger.error(f"Error listando aplicaciones abiertas: {e}")
        return False, []
