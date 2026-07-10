"""
actions/system.py
Control del sistema operativo Windows: volumen, capturas de pantalla,
información del sistema, apagar/reiniciar/suspender.
"""

import os
import subprocess
import psutil
from datetime import datetime
from config import TEMP_DIR
from modules.logger import get_logger

logger = get_logger()


def ajustar_volumen(porcentaje):
    """
    Ajusta el volumen maestro del sistema a un porcentaje (0-100).
    Usa nircmd si está disponible, o pycaw como alternativa más nativa de Windows.
    """
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        dispositivos = AudioUtilities.GetSpeakers()
        interfaz = dispositivos.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volumen = cast(interfaz, POINTER(IAudioEndpointVolume))

        nivel = max(0, min(100, int(porcentaje))) / 100.0
        volumen.SetMasterVolumeLevelScalar(nivel, None)

        logger.info(f"Volumen ajustado a {porcentaje}%")
        return True, f"Volumen ajustado a {porcentaje} por ciento."
    except ImportError:
        logger.warning("pycaw no instalado, no se puede ajustar el volumen. Instala con: pip install pycaw comtypes")
        return False, "No tengo el módulo necesario para ajustar el volumen. Necesitas instalar pycaw."
    except Exception as e:
        logger.error(f"Error ajustando volumen: {e}")
        return False, "No pude ajustar el volumen."


def tomar_captura_pantalla():
    """Toma una captura de pantalla y la guarda con timestamp en la carpeta temporal."""
    try:
        import pyautogui
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = os.path.join(TEMP_DIR, f"captura_{timestamp}.png")
        captura = pyautogui.screenshot()
        captura.save(ruta)
        logger.info(f"Captura de pantalla guardada: {ruta}")
        return True, f"Captura de pantalla guardada en {ruta}."
    except Exception as e:
        logger.error(f"Error tomando captura de pantalla: {e}")
        return False, "No pude tomar la captura de pantalla."


def info_sistema():
    """Obtiene información del sistema: uso de CPU, RAM y batería si aplica."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_porcentaje = ram.percent
        ram_usada_gb = round(ram.used / (1024 ** 3), 1)
        ram_total_gb = round(ram.total / (1024 ** 3), 1)

        info_texto = f"CPU al {cpu} por ciento. RAM usada: {ram_usada_gb} de {ram_total_gb} gigabytes ({ram_porcentaje} por ciento)."

        bateria = psutil.sensors_battery()
        if bateria:
            info_texto += f" Batería al {bateria.percent} por ciento."

        logger.info(f"Info del sistema consultada: {info_texto}")
        return True, info_texto
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        return False, "No pude obtener la información del sistema."


def apagar_equipo():
    """Apaga el equipo. Requiere doble confirmación gestionada en action_manager.py."""
    try:
        logger.warning("Apagando el equipo por solicitud del usuario.")
        subprocess.run(["shutdown", "/s", "/t", "5"], shell=True)
        return True, "Apagando el equipo en 5 segundos."
    except Exception as e:
        logger.error(f"Error apagando el equipo: {e}")
        return False, "No pude apagar el equipo."


def reiniciar_equipo():
    """Reinicia el equipo. Requiere doble confirmación gestionada en action_manager.py."""
    try:
        logger.warning("Reiniciando el equipo por solicitud del usuario.")
        subprocess.run(["shutdown", "/r", "/t", "5"], shell=True)
        return True, "Reiniciando el equipo en 5 segundos."
    except Exception as e:
        logger.error(f"Error reiniciando el equipo: {e}")
        return False, "No pude reiniciar el equipo."


def suspender_equipo():
    """Suspende el equipo (modo de bajo consumo)."""
    try:
        logger.info("Suspendiendo el equipo.")
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=True)
        return True, "Suspendiendo el equipo."
    except Exception as e:
        logger.error(f"Error suspendiendo el equipo: {e}")
        return False, "No pude suspender el equipo."
