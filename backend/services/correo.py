"""
Envío de mails por SMTP (decisión 030): el Gmail del proyecto con una contraseña de aplicación.
Sin SMTP_HOST (desarrollo y tests) el mail se escribe en el log en vez de enviarse.
"""

import logging
import smtplib
from email.message import EmailMessage

from backend.configuracion import SMTP_CONTRASENA, SMTP_HOST, SMTP_PORT, SMTP_USUARIO

logger = logging.getLogger(__name__)


def configurado() -> bool:
    """Si hay SMTP: sin él, los mails solo quedan en el log y no le llegan a nadie."""
    return bool(SMTP_HOST)


def enviar(destinatario: str, asunto: str, texto: str) -> None:
    if not SMTP_HOST:
        logger.warning("Mail sin enviar (falta SMTP_HOST) para %s: %s\n%s", destinatario, asunto, texto)
        return
    mensaje = EmailMessage()
    mensaje["From"] = f"Laboratorio Virtual Auditivo <{SMTP_USUARIO}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(texto)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USUARIO, SMTP_CONTRASENA)
        smtp.send_message(mensaje)
