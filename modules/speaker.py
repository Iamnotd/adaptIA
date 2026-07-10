"""
modules/speaker.py
Síntesis de voz: convierte texto en audio hablado.
Usa ElevenLabs si hay API key configurada (voz natural de alta calidad),
con respaldo automático a pyttsx3 (offline, gratis) si no está disponible.
"""

import pyttsx3

from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID
from modules.logger import get_logger

logger = get_logger()


class Speaker:
    """Gestiona la conversión de texto a voz, con ElevenLabs o pyttsx3 como respaldo."""

    def __init__(self):
        self.usar_elevenlabs = bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)
        if self.usar_elevenlabs:
            try:
                from elevenlabs.client import ElevenLabs
                from elevenlabs import play
                self.client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                self._play = play
                logger.info("Speaker configurado con ElevenLabs (voz de alta calidad).")
            except Exception as e:
                logger.warning(f"No se pudo inicializar ElevenLabs, usando pyttsx3: {e}")
                self.usar_elevenlabs = False

        if not self.usar_elevenlabs:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 175)
            # Intentar usar una voz en español si está disponible en el sistema
            for voz in self.engine.getProperty("voices"):
                if "spanish" in voz.name.lower() or "español" in voz.name.lower() or "es" in voz.id.lower():
                    self.engine.setProperty("voice", voz.id)
                    break
            logger.info("Speaker configurado con pyttsx3 (offline).")

    def hablar(self, texto):
        """Convierte el texto recibido en audio y lo reproduce."""
        if not texto:
            return
        logger.info(f"adaptIA dice: {texto}")
        try:
            if self.usar_elevenlabs:
                audio = self.client.generate(
                    text=texto,
                    voice=ELEVENLABS_VOICE_ID,
                    model="eleven_multilingual_v2"
                )
                self._play(audio)
            else:
                self.engine.say(texto)
                self.engine.runAndWait()
        except Exception as e:
            logger.exception(f"Error al reproducir voz: {e}")
            # Respaldo de emergencia si ElevenLabs falla en tiempo real
            try:
                engine = pyttsx3.init()
                engine.say(texto)
                engine.runAndWait()
            except Exception as e2:
                logger.exception(f"Error también en el respaldo pyttsx3: {e2}")
