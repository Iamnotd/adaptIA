"""
modules/executor.py
Ejecutor central: recibe una intención YA CONFIRMADA por el usuario y llama
a la función correspondiente del directorio actions/.
"""

from actions import apps, browser, communicator, files, system
from modules.logger import get_logger

logger = get_logger()


class Executor:
    """Despacha cada intención confirmada a su función correspondiente con manejo de errores."""

    def ejecutar(self, intencion, parametros):
        """
        Ejecuta la acción según la intención. Devuelve (exitoso: bool, mensaje: str).
        Cualquier excepción es capturada para que adaptIA nunca se caiga por un error
        en una acción individual.
        """
        parametros = parametros or {}

        try:
            objetivo = parametros.get("objetivo", "")
            contenido = parametros.get("contenido", "")
            destinatario = parametros.get("destinatario", "")
            asunto = parametros.get("asunto", "Mensaje de adaptIA")

            if intencion == "abrir_app":
                return apps.abrir_app(objetivo)

            elif intencion == "cerrar_app":
                return apps.cerrar_app(objetivo)

            elif intencion == "abrir_web":
                return browser.abrir_url(objetivo)

            elif intencion == "buscar_web":
                return browser.buscar_en_web(contenido or objetivo)

            elif intencion == "enviar_correo":
                return communicator.enviar_correo(destinatario, asunto, contenido)

            elif intencion == "enviar_sms":
                return communicator.enviar_sms(destinatario, contenido)

            elif intencion == "enviar_whatsapp":
                return communicator.enviar_whatsapp(destinatario, contenido)

            elif intencion == "llamar":
                return communicator.realizar_llamada(destinatario, contenido or "Llamada iniciada por adaptIA.")

            elif intencion == "gestion_archivos":
                accion_archivo = parametros.get("accion_archivo", "buscar")
                if accion_archivo == "crear_carpeta":
                    return files.crear_carpeta(objetivo)
                elif accion_archivo == "eliminar":
                    return files.eliminar_archivo(objetivo)
                elif accion_archivo == "abrir":
                    return files.abrir_archivo(objetivo)
                else:
                    return files.buscar_archivo(objetivo)

            elif intencion == "control_sistema":
                if objetivo == "apagar_equipo":
                    return system.apagar_equipo()
                elif objetivo == "reiniciar_equipo":
                    return system.reiniciar_equipo()
                elif objetivo == "suspender_equipo":
                    return system.suspender_equipo()
                elif objetivo == "captura_pantalla":
                    return system.tomar_captura_pantalla()
                elif objetivo == "info_sistema":
                    return system.info_sistema()
                elif objetivo == "volumen":
                    return system.ajustar_volumen(contenido)
                else:
                    return False, "No reconozco esa acción de sistema."

            else:
                logger.warning(f"Intención no implementada en executor: {intencion}")
                return False, "Esa acción todavía no está disponible."

        except Exception as e:
            logger.exception(f"Error ejecutando acción '{intencion}': {e}")
            return False, "Ocurrió un error inesperado al ejecutar la acción."
