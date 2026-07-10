"""
modules/action_manager.py
Gestor de confirmación: NUNCA ejecuta una acción directamente.
Antes de ejecutar, le dice al usuario qué acción está a punto de realizar
y espera una respuesta verbal de confirmación o cancelación.

Acciones especialmente sensibles (apagar/reiniciar el equipo) requieren
una doble confirmación por seguridad.
"""

import os

from config import CONFIRM_WORDS, CANCEL_WORDS, TEMP_DIR
from modules.logger import get_logger

logger = get_logger()

ACCIONES_DOBLE_CONFIRMACION = {"apagar_equipo", "reiniciar_equipo"}


class ActionManager:
    """
    Orquesta el flujo: anunciar la acción -> escuchar confirmación -> ejecutar o cancelar.
    Depende de un objeto 'speaker' (voz), 'listener' (escucha) y 'transcriber' (texto)
    que se le inyectan desde main.py.
    """

    def __init__(self, speaker, listener, transcriber, executor):
        self.speaker = speaker
        self.listener = listener
        self.transcriber = transcriber
        self.executor = executor

    def _escuchar_respuesta_si_no(self):
        """Graba y transcribe una respuesta corta del usuario (sí/no)."""
        audio = self.listener.grabar_comando()
        if audio is None:
            logger.warning("No se recibió audio para la confirmación.")
            return ""

        ruta_temp = os.path.join(TEMP_DIR, "confirmacion.wav")
        if not self.listener.guardar_audio_temporal(audio, ruta_temp):
            logger.warning("No se pudo guardar el audio de confirmación.")
            return ""

        texto, _ = self.transcriber.transcribir(ruta_temp)
        return texto.lower().strip()

    def _es_confirmacion(self, texto):
        return any(palabra in texto for palabra in CONFIRM_WORDS)

    def _es_cancelacion(self, texto):
        return any(palabra in texto for palabra in CANCEL_WORDS)

    def procesar_intencion(self, data_intencion):
        """
        Recibe el JSON de intención clasificado por brain.py y gestiona
        todo el flujo de confirmación antes de ejecutar la acción real.
        """
        if not isinstance(data_intencion, dict):
            logger.error(f"Intención inválida recibida: {data_intencion}")
            self.speaker.hablar("No pude interpretar ese comando.")
            return "desconocido", {}, "Intención inválida.", False

        intencion = data_intencion.get("intencion", "desconocido")

        # Caso: solo conversación, no requiere confirmación ni ejecución de acciones
        if intencion == "conversacion":
            respuesta = data_intencion.get("respuesta_hablada", "")
            if respuesta:
                self.speaker.hablar(respuesta)
            return intencion, data_intencion.get("parametros", {}), respuesta, True

        if intencion == "desconocido":
            self.speaker.hablar(data_intencion.get("respuesta_hablada", "No entendí ese comando."))
            return intencion, {}, "No se reconoció el comando.", False

        if not data_intencion.get("confirmacion_requerida", False):
            logger.warning(
                f"La intención accionable '{intencion}' llegó sin confirmación requerida. "
                "Se pedirá confirmación por seguridad."
            )

        # Anunciar la acción y pedir confirmación
        mensaje_confirmacion = data_intencion.get("mensaje_confirmacion") or "¿Confirmas esta acción?"
        self.speaker.hablar(mensaje_confirmacion)

        respuesta_usuario = self._escuchar_respuesta_si_no()
        logger.info(f"Respuesta de confirmación del usuario: '{respuesta_usuario}'")

        if not self._es_confirmacion(respuesta_usuario):
            if self._es_cancelacion(respuesta_usuario):
                logger.info("El usuario canceló explícitamente la acción.")
            else:
                logger.info("La respuesta no fue una confirmación clara; se cancela la acción.")
            self.speaker.hablar("De acuerdo, he cancelado la acción.")
            return intencion, data_intencion.get("parametros", {}), "Acción cancelada por el usuario.", False

        # Doble confirmación para acciones críticas (apagar, reiniciar)
        if intencion == "control_sistema" and data_intencion.get("parametros", {}).get("objetivo") in ACCIONES_DOBLE_CONFIRMACION:
            self.speaker.hablar("Esta acción cerrará tus programas abiertos. ¿Estás completamente seguro?")
            segunda_respuesta = self._escuchar_respuesta_si_no()
            if not self._es_confirmacion(segunda_respuesta):
                self.speaker.hablar("Acción cancelada por seguridad.")
                return intencion, data_intencion.get("parametros", {}), "Cancelada en doble confirmación.", False

        # Ejecutar la acción real
        exitoso, resultado_texto = self.executor.ejecutar(intencion, data_intencion.get("parametros", {}))
        self.speaker.hablar(resultado_texto)

        return intencion, data_intencion.get("parametros", {}), resultado_texto, exitoso
