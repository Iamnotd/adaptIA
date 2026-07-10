"""
modules/listener.py
Captura de audio en tiempo real con microfono siempre abierto.
Detecta la palabra clave "Orion" y graba el comando completo del usuario.
Usa automaticamente el microfono predeterminado del sistema Windows.
"""

import speech_recognition as sr
import unicodedata
import os
from config import WAKE_WORD, SILENCE_THRESHOLD_SECONDS, MAX_RECORDING_SECONDS
from modules.logger import get_logger

logger = get_logger()


def _normalizar(texto):
    """Quita acentos y pasa a minusculas para comparar la palabra clave."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


def _obtener_indice_microfono_principal():
    """Busca automaticamente el mejor microfono disponible."""
    nombres_prioritarios = [
        "microphone array (amd",
        "microfono (realtek",
        "microphone (realtek",
        "microphone array",
        "built-in microphone",
    ]
    nombres_excluir = [
        "mezcla", "stereo mix", "output", "altavoz", "speaker",
        "headphones", "auriculares", "virtual", "asignador"
    ]

    micros = sr.Microphone.list_microphone_names()
    for i, nombre in enumerate(micros):
        nombre_lower = nombre.lower()
        if any(excluir in nombre_lower for excluir in nombres_excluir):
            continue
        for prioritario in nombres_prioritarios:
            if prioritario in nombre_lower:
                logger.info(f"Microfono seleccionado: [{i}] {nombre}")
                return i

    logger.info("Usando microfono predeterminado del sistema.")
    return None


class Listener:
    """Gestiona el microfono en modo de escucha pasiva continua."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = SILENCE_THRESHOLD_SECONDS

        indice = _obtener_indice_microfono_principal()
        if indice is not None:
            self.microphone = sr.Microphone(device_index=indice)
        else:
            self.microphone = sr.Microphone()

        logger.info("Calibrando microfono...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        logger.info("Microfono listo. Orion esta en escucha pasiva.")

    def esperar_palabra_clave(self):
        """Escucha continuamente esperando la palabra clave 'Orion'."""
        with self.microphone as source:
            while True:
                try:
                    audio = self.recognizer.listen(
                        source, timeout=None, phrase_time_limit=3
                    )
                    texto = self.recognizer.recognize_google(audio, language="es-ES")
                    texto_normalizado = _normalizar(texto)
                    logger.debug(f"Escucha pasiva: '{texto}'")
                    if WAKE_WORD in texto_normalizado:
                        logger.info("Palabra clave 'Orion' detectada.")
                        return True
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    logger.error(f"Error de conexion: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error en escucha pasiva: {e}")
                    continue

    def grabar_comando(self):
        """Graba el comando del usuario tras activarse con 'Orion'."""
        with self.microphone as source:
            logger.info("Escuchando comando...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=MAX_RECORDING_SECONDS
                )
                logger.info("Comando grabado.")
                return audio
            except sr.WaitTimeoutError:
                logger.warning("Tiempo de espera agotado.")
                return None

    def guardar_audio_temporal(self, audio, ruta_wav):
        """Guarda el audio capturado como archivo .wav temporal para Whisper."""
        try:
            ruta_abs = os.path.abspath(ruta_wav)
            carpeta = os.path.dirname(ruta_abs)
            os.makedirs(carpeta, exist_ok=True)
            with open(ruta_abs, "wb") as f:
                f.write(audio.get_wav_data())
            logger.info(f"Audio guardado en: {ruta_abs}")
            return ruta_abs
        except Exception as e:
            logger.error(f"Error guardando audio: {e}")
            return None
