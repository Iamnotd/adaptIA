"""Captura de audio y detección de la palabra de activación Orion."""

import os
import unicodedata
import speech_recognition as sr
from config import WAKE_WORD, SILENCE_THRESHOLD_SECONDS, MAX_RECORDING_SECONDS
from modules.logger import get_logger

logger = get_logger()


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def listar_microfonos():
    try:
        return sr.Microphone.list_microphone_names()
    except Exception as exc:
        logger.error(f"No se pudieron listar los microfonos: {exc}")
        return []


def _obtener_indice_microfono_principal():
    nombres_prioritarios = [
        "microphone array", "microfono", "microphone", "realtek", "built-in"
    ]
    nombres_excluir = [
        "mezcla", "stereo mix", "output", "altavoz", "speaker",
        "headphones", "auriculares", "virtual", "asignador"
    ]
    micros = listar_microfonos()
    for i, nombre in enumerate(micros):
        bajo = nombre.lower()
        if any(x in bajo for x in nombres_excluir):
            continue
        if any(x in bajo for x in nombres_prioritarios):
            logger.info(f"Microfono seleccionado: [{i}] {nombre}")
            return i
    logger.info("Usando el microfono predeterminado de Windows.")
    return None


class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = SILENCE_THRESHOLD_SECONDS
        self.recognizer.non_speaking_duration = 0.5

        indice = _obtener_indice_microfono_principal()
        try:
            self.microphone = sr.Microphone(device_index=indice) if indice is not None else sr.Microphone()
        except Exception as exc:
            raise RuntimeError(
                "No pude abrir el microfono. Revisa permisos de Windows y la instalacion de PyAudio."
            ) from exc

        logger.info("Calibrando microfono durante 1 segundo...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        logger.info(f"Microfono listo. Umbral de energia: {self.recognizer.energy_threshold:.0f}")

    def esperar_palabra_clave(self):
        """Devuelve el texto reconocido cuando contiene Orion."""
        logger.info("Escucha pasiva: di 'Orion'.")
        with self.microphone as source:
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    texto = self.recognizer.recognize_google(audio, language="es-GT")
                    logger.info(f"Escucha pasiva reconocio: '{texto}'")
                    if WAKE_WORD in _normalizar(texto):
                        logger.info("Palabra clave Orion detectada.")
                        return texto
                except sr.WaitTimeoutError:
                    logger.debug("Sin voz; Orion sigue escuchando.")
                except sr.UnknownValueError:
                    logger.debug("Audio no entendible durante escucha pasiva.")
                except sr.RequestError as exc:
                    logger.error(f"Google Speech no esta disponible: {exc}")
                    raise RuntimeError("No hay conexion para detectar la palabra Orion.") from exc

    def grabar_comando(self):
        with self.microphone as source:
            logger.info("Escuchando comando...")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=MAX_RECORDING_SECONDS)
                logger.info("Comando grabado.")
                return audio
            except sr.WaitTimeoutError:
                logger.warning("No se detecto voz durante 10 segundos.")
                return None

    def guardar_audio_temporal(self, audio, ruta_wav):
        try:
            ruta_abs = os.path.abspath(ruta_wav)
            os.makedirs(os.path.dirname(ruta_abs), exist_ok=True)
            with open(ruta_abs, "wb") as archivo:
                archivo.write(audio.get_wav_data(convert_rate=16000, convert_width=2))
            logger.info(f"Audio guardado en: {ruta_abs}")
            return ruta_abs
        except Exception as exc:
            logger.error(f"Error guardando audio: {exc}")
            return None
