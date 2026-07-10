"""
main.py
Punto de entrada principal de adaptIA.
"""

import os
import sys
import threading

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

# Ruta del audio temporal SIN espacios
RUTA_AUDIO = os.path.join(TEMP_DIR, "comando.wav")


def ciclo_voz():
    """Ciclo principal de escucha y procesamiento de voz."""
    logger.info(f"Iniciando {ASSISTANT_NAME}...")

    speaker = Speaker()
    listener = Listener()
    transcriber = Transcriber()
    brain = Brain()
    memory = MemoryManager()
    executor = Executor()
    action_manager = ActionManager(speaker, listener, transcriber, executor)

    speaker.hablar("Orion esta activo y listo. Di Orion para activarme.")

    try:
        while True:
            # 1. Esperar palabra clave
            listener.esperar_palabra_clave()
            speaker.hablar("Dime.")

            # 2. Grabar comando
            audio = listener.grabar_comando()
            if audio is None:
                speaker.hablar("No escuche nada.")
                continue

            # 3. Guardar audio en ruta sin espacios
            ruta_guardada = listener.guardar_audio_temporal(audio, RUTA_AUDIO)
            if not ruta_guardada:
                speaker.hablar("Tuve un problema con el audio.")
                continue

            # 4. Transcribir
            texto_usuario, confianza = transcriber.transcribir(ruta_guardada)
            if not texto_usuario:
                speaker.hablar("No logre entender, intenta de nuevo.")
                continue

            if confianza < MIN_TRANSCRIPTION_CONFIDENCE:
                speaker.hablar("No estoy seguro de haber entendido, puedes repetirlo?")
                continue

            logger.info(f"Usuario dijo: '{texto_usuario}'")

            # 5. Clasificar intencion con Groq
            contexto = memory.obtener_contexto_reciente()
            data_intencion = brain.procesar(texto_usuario, contexto)

            # 6. Confirmar y ejecutar
            intencion, parametros, resultado, exitoso = action_manager.procesar_intencion(data_intencion)

            # 7. Guardar en memoria
            memory.guardar_interaccion(texto_usuario, intencion, parametros, resultado, exitoso)

    except KeyboardInterrupt:
        logger.info("Orion detenido.")
        speaker.hablar("Hasta luego.")
    except Exception as e:
        logger.exception(f"Error crítico en el ciclo de voz: {e}")
        speaker.hablar("Tuve un error crítico.")
    finally:
        memory.cerrar()


if __name__ == "__main__":
    try:
        from menu import iniciar_menu
        hilo_voz = threading.Thread(target=ciclo_voz, daemon=True)
        hilo_voz.start()
        iniciar_menu()
    except Exception as e:
        logger.warning(f"Menú no disponible, corriendo sin interfaz: {e}")
        ciclo_voz()
