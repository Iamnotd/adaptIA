"""
actions/communicator.py
Acciones de comunicación: correos, SMS, WhatsApp y llamadas telefónicas.
Correos vía SMTP/IMAP. SMS, WhatsApp y llamadas vía Twilio API.
"""

import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    EMAIL_ADDRESS, EMAIL_PASSWORD, EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_WHATSAPP_NUMBER
)
from modules.logger import get_logger

logger = get_logger()


def enviar_correo(destinatario, asunto, contenido):
    """Envía un correo electrónico usando SMTP (configurado para Gmail por defecto)."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return False, "No tengo configuradas las credenciales de correo. Revisa el archivo .env"

    try:
        mensaje = MIMEMultipart()
        mensaje["From"] = EMAIL_ADDRESS
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto
        mensaje.attach(MIMEText(contenido, "plain", "utf-8"))

        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            servidor.send_message(mensaje)

        logger.info(f"Correo enviado a {destinatario}")
        return True, f"Correo enviado a {destinatario} correctamente."
    except Exception as e:
        logger.error(f"Error enviando correo: {e}")
        return False, "No pude enviar el correo. Verifica las credenciales o la conexión."


def leer_correos_recientes(cantidad=5):
    """Lee los últimos correos no leídos de la bandeja de entrada vía IMAP."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return False, "No tengo configuradas las credenciales de correo."

    try:
        imap_server = EMAIL_SMTP_SERVER.replace("smtp", "imap")
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        _, datos = mail.search(None, "UNSEEN")
        ids_correos = datos[0].split()[-cantidad:]

        resumenes = []
        for id_correo in reversed(ids_correos):
            _, msg_data = mail.fetch(id_correo, "(RFC822)")
            mensaje = email_lib.message_from_bytes(msg_data[0][1])
            remitente = mensaje.get("From", "Desconocido")
            asunto = mensaje.get("Subject", "Sin asunto")
            resumenes.append(f"De {remitente}: {asunto}")

        mail.logout()
        return True, resumenes
    except Exception as e:
        logger.error(f"Error leyendo correos: {e}")
        return False, []


def _cliente_twilio():
    """Crea y devuelve un cliente de Twilio si las credenciales están configuradas."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        return None
    from twilio.rest import Client
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def enviar_sms(numero_destino, contenido):
    """Envía un SMS usando la API de Twilio."""
    cliente = _cliente_twilio()
    if not cliente:
        return False, "No tengo configuradas las credenciales de Twilio. Revisa el archivo .env"

    try:
        mensaje = cliente.messages.create(
            body=contenido,
            from_=TWILIO_PHONE_NUMBER,
            to=numero_destino
        )
        logger.info(f"SMS enviado a {numero_destino}, SID: {mensaje.sid}")
        return True, f"SMS enviado a {numero_destino}."
    except Exception as e:
        logger.error(f"Error enviando SMS: {e}")
        return False, "No pude enviar el SMS. Verifica el número y las credenciales."


def enviar_whatsapp(numero_destino, contenido):
    """Envía un mensaje de WhatsApp usando el Sandbox de Twilio."""
    cliente = _cliente_twilio()
    if not cliente:
        return False, "No tengo configuradas las credenciales de Twilio. Revisa el archivo .env"

    try:
        if not numero_destino.startswith("whatsapp:"):
            numero_destino = f"whatsapp:{numero_destino}"

        mensaje = cliente.messages.create(
            body=contenido,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=numero_destino
        )
        logger.info(f"WhatsApp enviado a {numero_destino}, SID: {mensaje.sid}")
        return True, f"WhatsApp enviado a {numero_destino}."
    except Exception as e:
        logger.error(f"Error enviando WhatsApp: {e}")
        return False, "No pude enviar el WhatsApp. Verifica el número y las credenciales."


def realizar_llamada(numero_destino, mensaje_voz="Llamada iniciada por adaptIA."):
    """Realiza una llamada telefónica usando Twilio, reproduciendo un mensaje de texto a voz."""
    cliente = _cliente_twilio()
    if not cliente:
        return False, "No tengo configuradas las credenciales de Twilio. Revisa el archivo .env"

    try:
        twiml = f"<Response><Say language='es-MX'>{mensaje_voz}</Say></Response>"
        llamada = cliente.calls.create(
            twiml=twiml,
            from_=TWILIO_PHONE_NUMBER,
            to=numero_destino
        )
        logger.info(f"Llamada iniciada a {numero_destino}, SID: {llamada.sid}")
        return True, f"Llamando a {numero_destino}."
    except Exception as e:
        logger.error(f"Error realizando llamada: {e}")
        return False, "No pude realizar la llamada. Verifica el número y las credenciales."
