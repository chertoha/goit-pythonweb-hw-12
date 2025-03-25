"""
Configuration settings module.

This module defines the `Settings` class, which loads configuration values from environment variables
and provides access to various application settings, including database, JWT, email, and cloud storage configurations.

Attributes:
    DB_URL: Database connection URL.
    JWT_SECRET: JWT secret key for signing tokens.
    JWT_ALGORITHM: JWT signing algorithm (default: "HS256").
    JWT_EXPIRATION_SECONDS: JWT expiration time in seconds (default: 3600).
    MAIL_USERNAME: Email server username for sending emails.
    MAIL_PASSWORD: Email server password for sending emails.
    MAIL_FROM: Default "from" email address for sending emails.
    MAIL_PORT: Email server port.
    MAIL_SERVER: Email server host.
    MAIL_FROM_NAME: Display name for sent emails.
    MAIL_STARTTLS: Boolean to enable STARTTLS for email.
    MAIL_SSL_TLS: Boolean to enable SSL/TLS for email.
    USE_CREDENTIALS: Boolean to enable using credentials for email.
    VALIDATE_CERTS: Boolean to validate email server certificates.
    CLD_NAME: Cloud service name for file storage.
    CLD_API_KEY: Cloud API key.
    CLD_API_SECRET: Cloud API secret.
"""

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "Rest API Chertok Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
