"""Punto de entrada principal de Orion adaptIA."""
import os
import sys
import threading
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import ASSISTANT_NAME, TEMP_DIR, MIN_TRANSCRIPTION_CONFIDENCE
from modules.logger import get_logger
from modules.listener import Listener
from modules.transcriber import Transcriber
from modules.brain import Brain
from modules.speaker import Speaker
from modules.memory import MemoryManager
from modules.action_manager import ActionManager
from modules.executor import Executor

logger = get_logger()
RUTA_AUDIO = os.path.join(TEMP_DIR, "comando.wav")


def _ui_estado(texto, activo=False):
    try:
        from menu import actualizar_estado_menu, log_menu
        actualizar_estado_menu(texto, activo)
        log_menu(texto)
    except Exception:
        pass


def ciclo_voz():
    memory = None
    speaker = None
    try:
        _ui_estado("INICIANDO ORION")
        logger.info(f"Iniciando {ASSISTANT_NAME}...")
        speaker = Speaker()
        _ui_estado("CARGANDO MICROFONO")
        listener = Listener()
        _ui_estado("CARGANDO WHISPER")
        transcriber = Transcriber()
        brain = Brain()
        memory = MemoryManager()
        executor = Executor()
        action_manager = ActionManager(speaker, listener, transcriber, executor)

        speaker.hablar("Orion esta activo. Di Orion para activarme.")
        while True:
            _ui_estado("ESCUCHA PASIVA")
            listener.esperar_palabra_clave()
            _ui_estado("ACTIVADO", True)
            speaker.hablar("Dime.")

            audio = listener.grabar_comando()
            if audio is None:
                speaker.hablar("No escuche nada.")
                continue
            ruta = listener.guardar_audio_temporal(audio, RUTA_AUDIO)
            if not ruta:
                speaker.hablar("Tuve un problema guardando el audio.")
                continue

            _ui_estado("TRANSCRIBIENDO", True)
            texto_usuario, confianza = transcriber.transcribir(ruta)
            if not texto_usuario:
                speaker.hablar("No logre entender. Intenta de nuevo.")
                continue
            logger.info(f"Usuario dijo: '{texto_usuario}'")
            _ui_estado(f"COMANDO: {texto_usuario[:35]}", True)

            # Whisper puede dar confianza conservadora; solo rechazamos valores extremadamente bajos.
            if confianza < max(0.15, MIN_TRANSCRIPTION_CONFIDENCE - 0.25):
                speaker.hablar("No estoy seguro de haber entendido. Puedes repetirlo?")
                continue

            contexto = memory.obtener_contexto_reciente()
            data_intencion = brain.procesar(texto_usuario, contexto)
            intencion, parametros, resultado, exitoso = action_manager.procesar_intencion(data_intencion)
            memory.guardar_interaccion(texto_usuario, intencion, parametros, resultado, exitoso)

    except Exception as exc:
        mensaje = f"ERROR DE VOZ: {exc}"
        logger.error(mensaje)
        logger.error(traceback.format_exc())
        _ui_estado(mensaje[:55])
        if speaker:
            try:
                speaker.hablar("Orion encontro un error. Revisa la consola.")
            except Exception:
                pass
    finally:
        if memory:
            memory.cerrar()


if __name__ == "__main__":
    try:
        from menu import iniciar_menu
        threading.Thread(target=ciclo_voz, daemon=True, name="OrionVoice").start()
        iniciar_menu()
    except Exception as exc:
        logger.warning(f"Menu no disponible; ejecutando solo consola: {exc}")
        ciclo_voz()
