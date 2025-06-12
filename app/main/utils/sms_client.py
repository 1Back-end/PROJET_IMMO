
import requests
import json
from app.main.core.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NexahUtils:
    @staticmethod
    def send_sms(phonenumber: str, body: str):
        try:
            url = "https://smsvas.com/bulk/public/index.php/api/v1/sendsms"
            payload = json.dumps({
                "user": Config.SMS_USER,
                "password": Config.SMS_PASSWORD,
                "senderid": Config.SMS_SENDER,
                "sms": body,
                "mobiles": phonenumber
            })
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 404:
                raise Exception("SMS not found")
            logger.info(response.json())
        except Exception as e:
            logger.error(str(e))
