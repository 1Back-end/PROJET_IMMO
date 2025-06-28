import smtplib
import logging
from email import encoders
from email.mime.base import MIMEBase
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from app.main.core.config import Config

def send_account_creation_email(email_to: str, first_name: str, last_name: str, password: str) -> None:
    try:
        # Chargement du template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "account_creation.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            first_name=first_name,
            last_name=last_name,
            password=password,
            project_name=Config.PROJECT_NAME
        )

        # Création de l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Compte créé"
        msg.attach(MIMEText(html_content, "html"))

        # Connexion et envoi
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")

def send_reset_password_option2_email(email_to: str, name: str,  otp: str):
    try:
        # Chargement du template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "reset_password_option2.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name,
            otp=otp,
            project_name=Config.PROJECT_NAME
        )

        # Création de l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Réinitialisation du mot de passe"
        msg.attach(MIMEText(html_content, "html"))

        # Connexion et envoi
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")


def send_start_reset_password(email_to: str, name: str, code: str) -> None:
    try:
        # Charger le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "start_reset_password.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name,
            code=code,
            project_name=Config.PROJECT_NAME
        )

        # Créer l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Réinitialisation du mot de passe"
        msg.attach(MIMEText(html_content, "html"))

        # Connexion et envoi
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")


def notify_owner_new_licence(email_to: str, name: str, licence: str, service: str):
    try:
        licence_text = f"""LICENCE DETAILS

Propriétaire : {name}
Service : {service}
Clé de licence : {licence}

Généré via {Config.PROJECT_NAME}
"""

        print("[DEBUG] Création du message email")
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Nouvelle licence générée"

        body = f"Bonjour {name},\n\nVotre licence a été générée avec succès.\nVeuillez trouver le fichier joint.\n\nCordialement,\n{Config.PROJECT_NAME}"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(licence_text.encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=licence.txt")
        msg.attach(part)

        print("[DEBUG] Connexion au serveur SMTP")
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.set_debuglevel(1)
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(Config.EMAILS_FROM_EMAIL, email_to, msg.as_string())
        print("[DEBUG] Mail envoyé avec succès à", email_to)
    except Exception as e:
        print(f"[MAIL ERROR] {e}")





def send_new_request(email_to: str, title:str,type:str,description:str) -> None:
    try:
        # Charger le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "new_request_licence.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            title=title,
            type=type,
            description=description,
            project_name=Config.PROJECT_NAME
        )

        # Créer l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Nouvelle demande de {type}"
        msg.attach(MIMEText(html_content, "html"))

        # Connexion et envoi
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")
