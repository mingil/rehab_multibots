import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config
from logger import log

def send_telegram(msg):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID: return
    
    tg_domain = "api.telegram.org"
    url = f"https://{tg_domain}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    parts = msg.split('\n\n')
    chunk = ""
    for part in parts:
        if len(chunk) + len(part) > 3500:
            try: requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
            except Exception as e: log.error(f"텔레그램 전송 에러: {e}")
            chunk = part + "\n\n"
            time.sleep(1)
        else:
            chunk += part + "\n\n"
    if chunk.strip():
        try: requests.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
        except Exception as e: log.error(f"텔레그램 전송 에러: {e}")

def send_email(subject, html_body):
    if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD: return
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.GMAIL_ADDRESS
    msg.attach(MIMEText(html_body, "html"))

    try:
        gmail_host = "smtp.gmail.com"
        with smtplib.SMTP_SSL(gmail_host, 465) as server:
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        log.error(f"이메일 전송 실패: {e}")

def notify_all(subject, tg_msg, html_body):
    send_telegram(tg_msg)
    send_email(subject, html_body)
