import smtplib
import ssl
import logging
from pathlib import Path
from typing import List
from email.header import Header
from email.message import EmailMessage
from pydantic import BaseModel
from logutils import get_logger


class SimpleSmtpData(BaseModel):
    host: str
    port: int


class SslSmtpData(BaseModel):
    host: str
    port: int
    user: str
    pwd: str


logger = get_logger(__name__, colored="light")


def send_email(
    recipients: List[str],
    sender: str,
    subject: str,
    smtp_data: SimpleSmtpData | SslSmtpData,
    bodytxt: str | None = None,
    bodyhtml: str | None = None,
    reply_addr: str | None = None,
    bcc: List[str] = [],
    unsubscribe_url: str | None = None,
    attachment: Path | None = None,
    logger: logging.Logger = logging.getLogger(),
    dry_run: bool = False,
    sender_header: str | None = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = str(Header(subject, "utf-8"))
    if sender_header is not None:
        msg["From"] = sender_header
    else:
        msg["From"] = sender
    msg["To"] = ",".join(recipients)
    if reply_addr:
        msg["Reply-To"] = reply_addr
    if unsubscribe_url:
        msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"

    if bodytxt:
        msg.set_content(bodytxt, subtype="plain")
    if bodyhtml:
        msg.add_alternative(bodyhtml, subtype="html")

    if attachment:
        logger.info(f"Attaching {attachment} to the email")
        with open(attachment, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="octet-stream",
                filename=attachment.name,
            )

    try:
        if isinstance(smtp_data, SslSmtpData):
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_data.host, smtp_data.port) as server:
                server.starttls(context=context)
                server.login(smtp_data.user, smtp_data.pwd)
                logger.info(
                    f"Sending email.\nSubject: {subject}.\nTo: {recipients}.\nBCC: {bcc}.\nSSL active"
                )
                if not dry_run:
                    server.sendmail(sender, recipients + bcc, msg.as_string())
        else:
            server = smtplib.SMTP(smtp_data.host, smtp_data.port)
            logger.info(
                f"Sending email.\nSubject: {subject}.\nTo: {recipients}.\nBCC: {bcc}"
            )
            if not dry_run:
                server.sendmail(sender, recipients + bcc, msg.as_string())
            server.quit()
    except Exception as e:
        logger.error(f"Failed to send mail to {msg['To']}")
        logger.exception(msg.as_string())
        raise e

    return msg
