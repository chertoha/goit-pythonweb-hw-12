"""
Module for handling email-related services.

This module provides functionalities related to sending emails, such as
sending a confirmation email for email verification. It uses the FastAPI Mail
package for sending emails asynchronously. The module also includes a utility
to generate email verification tokens.

Functions:
    - send_email: Sends a confirmation email with a verification token to the user's email address.
    - create_email_token: Generates a JWT token for email verification.
    - get_email_from_token: Decodes an email verification token to retrieve the email address.
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)

async def send_email(email: EmailStr, username: str, host: str):
    """
        Sends an email with a verification link to the provided email address.

        This function generates a JWT token for email verification and sends an
        email with a confirmation link to the user's email address using FastAPI Mail.

        Args:
            email (EmailStr): The recipient's email address.
            username (str): The recipient's username.
            host (str): The host domain where the verification link should point to.

        Raises:
            ConnectionErrors: If there is an issue with the email connection.
    """
    try:
        # Generate an email verification token
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Send the email message
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
