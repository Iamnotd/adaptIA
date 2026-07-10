"""
modules/transcriber.py
Transcripción de audio a texto usando Whisper (OpenAI), ejecutado localmente.
"""

import whisper
import os
from config import WHISPER_MODEL_SIZE, WHISPER_LANGUAGE, MIN_TRANSCRIPTION_CONFIDENCE
from modules.logger import get_logger

logger = get_logger()


class Transcriber:
    """Carga el modelo Whisper una sola vez y transcribe archivos de audio."""

    def __init__(self):
        logger.info(f"Cargando modelo Whisper '{WHISPER_MODEL_SIZE}'...")
        self.model = whisper.load_model(WHISPER_MODEL_SIZE)
        logger.info("Modelo Whisper cargado correctamente.")

    def transcribir(self, ruta_audio):
        """Transcribe un archivo de audio .wav a texto."""
        ruta_audio = os.path.abspath(ruta_audio)
        logger.debug(f"Buscando audio en: {ruta_audio}")

        if not os.path.exists(ruta_audio):
            logger.error(f"Archivo no encontrado: {ruta_audio}")
            return "", 0.0

        try:
            resultado = self.model.transcribe(
                ruta_audio,
                language=WHISPER_LANGUAGE,
                fp16=False
            )
            texto = resultado.get("text", "").strip()
            segmentos = resultado.get("segments", [])
            if segmentos:
                avg_logprob = sum(s.get("avg_logprob", -1) for s in segmentos) / len(segmentos)
                confianza = max(0.0, min(1.0, 1 + avg_logprob))
            else:
                confianza = 0.5
            logger.info(f"Transcripcion: '{texto}' (confianza: {confianza:.2f})")
            return texto, confianza
        except Exception as e:
            logger.error(f"Error transcribiendo audio: {e}")
            return "", 0.0
