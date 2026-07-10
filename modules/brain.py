"""
modules/brain.py
Cerebro principal de adaptIA: se comunica con la API de Groq (gratis)
usando el modelo LLaMA 3.3 70B para clasificar la intención del usuario
y generar respuestas en lenguaje natural.
"""

import json
import requests
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, ASSISTANT_NAME
from modules.logger import get_logger

logger = get_logger()

SYSTEM_PROMPT = f"""Eres {ASSISTANT_NAME}, un asistente de inteligencia artificial de escritorio para Windows.
Tu trabajo es interpretar lo que el usuario dice por voz y clasificarlo en una intención de acción concreta.

IMPORTANTE: Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto adicional, sin explicaciones,
sin marcadores de markdown como ```json. Solo el JSON puro.

El formato exacto debe ser:
{{
  "intencion": "abrir_app | cerrar_app | abrir_web | buscar_web | enviar_correo | enviar_sms | enviar_whatsapp | llamar | control_sistema | gestion_archivos | conversacion | desconocido",
  "parametros": {{
    "objetivo": "nombre de la app, URL, contacto o archivo segun aplique",
    "contenido": "cuerpo del mensaje, correo o texto a buscar segun aplique",
    "destinatario": "nombre, correo o numero de telefono si aplica",
    "asunto": "asunto del correo si aplica"
  }},
  "confirmacion_requerida": true,
  "mensaje_confirmacion": "Estoy a punto de [descripcion clara y natural en español de la accion]. ¿Confirmas?",
  "respuesta_hablada": "Respuesta corta y natural para decir en voz alta si la intencion es solo conversacion"
}}

Reglas:
- Si la intención es "conversacion" (el usuario solo quiere platicar o preguntar algo), pon confirmacion_requerida en false
  y responde de forma natural en "respuesta_hablada".
- Para cualquier otra intención que implique ejecutar una acción en el sistema, confirmacion_requerida siempre debe ser true.
- El mensaje_confirmacion debe ser claro, corto y en español natural, como si fueras a decirlo en voz alta.
- Si no entiendes el comando, usa intencion "desconocido" y pide aclaración en respuesta_hablada.
- Nunca agregues texto fuera del JSON.
"""


class Brain:
    """Gestiona la comunicación con la API de Groq para clasificar intenciones."""

    def __init__(self):
        if not GROQ_API_KEY:
            logger.error("GROQ_API_KEY no está configurada en el archivo .env")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    def procesar(self, texto_usuario, contexto_reciente=None):
        """
        Envía el texto del usuario a Groq junto con el contexto de interacciones
        recientes, y devuelve un diccionario con la intención clasificada.
        """
        contexto_texto = ""
        if contexto_reciente:
            lineas = []
            for c in contexto_reciente:
                lineas.append(f"Usuario dijo: {c['usuario']} -> Intención: {c['intencion']} -> Resultado: {c['resultado']}")
            contexto_texto = "Contexto de interacciones recientes:\n" + "\n".join(lineas) + "\n\n"

        prompt_usuario = f"{contexto_texto}Comando actual del usuario: \"{texto_usuario}\""

        payload = {
            "model": GROQ_MODEL,
            "max_tokens": MAX_TOKENS,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario}
            ]
        }

        try:
            respuesta = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            respuesta.raise_for_status()
            data_respuesta = respuesta.json()
            texto_respuesta = data_respuesta["choices"][0]["message"]["content"].strip()

            # Limpieza por si el modelo agrega marcadores de markdown
            if texto_respuesta.startswith("```"):
                texto_respuesta = texto_respuesta.strip("`")
                if texto_respuesta.startswith("json"):
                    texto_respuesta = texto_respuesta[4:].strip()

            data = json.loads(texto_respuesta)
            logger.debug(f"Intención clasificada por Groq: {data}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de Groq: {e} | Respuesta cruda: {texto_respuesta}")
            return self._respuesta_desconocida()
        except requests.exceptions.Timeout:
            logger.error("Timeout conectando con Groq API")
            return self._respuesta_desconocida(error=True)
        except Exception as e:
            logger.error(f"Error comunicándose con Groq API: {e}")
            return self._respuesta_desconocida(error=True)

    def _respuesta_desconocida(self, error=False):
        """Respuesta de respaldo cuando no se puede clasificar la intención."""
        mensaje = "Tuve un problema procesando tu solicitud." if error else "No entendí bien ese comando, ¿puedes repetirlo?"
        return {
            "intencion": "desconocido",
            "parametros": {},
            "confirmacion_requerida": False,
            "mensaje_confirmacion": "",
            "respuesta_hablada": mensaje
        }
