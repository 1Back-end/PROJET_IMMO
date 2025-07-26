import smtplib
import logging
from datetime import datetime
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





def send_new_request_extend(email_to: str, title:str,type:str,description:str,number_of_days:int) -> None:
    try:
        # Charger le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "new_request_licence_extend.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            title=title,
            type=type,
            description=description,
            number_of_days = number_of_days,
            project_name=Config.PROJECT_NAME
        )

        # Créer l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Nouvelle demande de prolongation de licence"
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


def send_notify_pending_request(email_to: str,title: str,licence_type: str,owner_name: str,service_name: str,licence_duration: str,description: str,
    created_at: str,status: str) -> None:
    try:
        # Charger le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "notify_request_licence.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        # Rendre le contenu HTML avec Jinja2
        html_content = template.render(
            title=title,
            type=licence_type,
            owner_name=owner_name,
            service_name=service_name,
            licence_duration=licence_duration,
            description=description,
            created_at=created_at,
            status=status,
            project_name=Config.PROJECT_NAME
        )

        # Préparer l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Demande de  {licence_type} non traité"
        msg.attach(MIMEText(html_content, "html"))

        # Envoyer l'email
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")

def send_account_confirmation_email(email_to: str, name: str, code: str, valid_minutes: int) -> None:
    try:
        # Charger le template HTML
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "user_action_validations.html"
        html_content = Template(template_path.read_text(encoding="utf-8")).render(
            name=name,
            code=code,
            valid_minutes=valid_minutes,
            project_name=Config.PROJECT_NAME
        )

        # Créer l'email
        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.EMAILS_FROM_NAME} | Activation de compte"
        msg.attach(MIMEText(html_content, "html"))

        # Connexion SMTP et envoi
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email : {e}")


def send_expiration_email(email_to: str, license_key: str, organisation_name: str, service_name: str, expires_at: str) -> None:
    try:
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "license_expired.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            license_key=license_key,
            organisation_name=organisation_name,
            service_name=service_name,
            expires_at=expires_at,
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | Votre licence est expirée"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email d'expiration envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email d'expiration : {e}")


def notify_new_company(email_to: str, title:str,description:str,created_by:str) -> None:
    try:
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "notify_new_company.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            title=title,
            description=description,
            created_by=created_by,
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | Nouvelle entreprise crée"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email d'expiration envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email d'expiration : {e}")


def send_organisation_otp(email_to: str, otp: str, expirate_at: datetime) -> None:
    try:
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "validate_organisation_otp.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            otp=otp,
            expirate_at=expirate_at.strftime("%d/%m/%Y à %H:%M"),
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | Code de validation d'organisation"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email OTP envoyé à {email_to}")
    except Exception as e:
        logging.error(f"❌ Erreur lors de l'envoi de l'email OTP : {e}")



def send_organisation_otp_to_user(email_to: str, otp: str, expirate_at: datetime) -> None:
    try:
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "validate_organisation_otp_code.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            otp=otp,
            expirate_at=expirate_at.strftime("%d/%m/%Y à %H:%M"),
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | Vérification de votre organisation"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email de vérification envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur envoi OTP à {email_to} : {e}")



def send_user_accepted_request(email_to: str, title: str,full_name:str,request_date:datetime) -> None:
    try:
        # Nouveau fichier template
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "licence_request_accepted.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            full_name=full_name,
            title=title,
            request_date=request_date.strftime("%d/%m/%Y <UNK> %H:%M"),
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | {title}"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email de vérification envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur envoi email à {email_to} : {e}")



def send_user_declined_request(email_to: str, title: str,full_name:str,request_date:datetime) -> None:
    try:
        # Nouveau fichier template
        template_path = Path(Config.EMAIL_TEMPLATES_DIR) / "licence_request_declined.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        html_content = template.render(
            full_name=full_name,
            title=title,
            request_date=request_date.strftime("%d/%m/%Y <UNK> %H:%M"),
            project_name=Config.PROJECT_NAME,
        )

        msg = MIMEMultipart()
        msg["From"] = f"{Config.EMAILS_FROM_NAME} <{Config.EMAILS_FROM_EMAIL}>"
        msg["To"] = email_to
        msg["Subject"] = f"{Config.PROJECT_NAME} | {title}"
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            if Config.SMTP_TLS:
                server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.send_message(msg)

        logging.info(f"✅ Email de vérification envoyé à {email_to}")

    except Exception as e:
        logging.error(f"❌ Erreur envoi email à {email_to} : {e}")
