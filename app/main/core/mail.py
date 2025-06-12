import smtplib
import logging
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from app.main.core.config import Config

def send_account_creation_email(email_to: str, first_name: str, last_name: str, password: str) -> None:
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "account_creation.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            first_name=first_name, last_name=last_name, password=password, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "UNIVERSITY GRADES MANAGEMENT SYSTEM. | Compte créé"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")

def send_account_owner_creation(email_to: str, firstname: str,  password: str):
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "account_owner_creation_.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            firstname=firstname,  password=password, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "UNIVERSITY GRADES MANAGEMENT SYSTEM. | Compte créé"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")


def send_student_matricule(email_to: str, name:str,matricule):
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "send_student_matricule.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name,  matricule=matricule, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "UNIVERSITY GRADES MANAGEMENT SYSTEM. | RECEPTION DU MATRICULE"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")

def send_reset_password_option2_email(email_to: str, name: str,  otp: str):
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "reset_password_option2.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name, otp=otp, project_name=Config.PROJECT_NAME
        )

        # Création et envoi de l'email
        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email_to, "UNIVERSITY GRADES MANAGEMENT SYSTEM | Réinitialisation du mot de passe"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")


def send_notification_to_candidate(email: str, name:str , job_title: str, job_description: str):
    try:
        # Charger et rendre le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "notification_to_candidate.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name, job_title=job_title, job_description=job_description, project_name=Config.PROJECT_NAME
        )

        msg = MIMEMultipart()
        msg["From"], msg["To"], msg["Subject"] = Config.EMAILS_FROM_CLOUDINARY, email, "UNIVERSITY GRADES MANAGEMENT SYSTEM. | Nouvelle offre d'emploi"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.MAILTRAP_HOST, Config.MAILTRAP_PORT) as server:
            server.starttls()
            server.login(Config.MAILTRAP_USERNAME, Config.MAILTRAP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email envoyé à {email}")

    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email : {e}")