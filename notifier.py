import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def get_retry_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def send_telegram(msg, log):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID: return
    tg_domain = "api.telegram.org"
    url = f"https://{tg_domain}/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    session = get_retry_session()

    parts = msg.split('\n\n')
    chunk = ""
    for part in parts:
        if len(chunk) + len(part) > 3500:
            try: session.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=15)
            except Exception as e: log.error(f"텔레그램 전송 에러: {e}")
            chunk = part + "\n\n"
            time.sleep(1)
        else:
            chunk += part + "\n\n"
    if chunk.strip():
        try: session.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": chunk, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=15)
        except Exception as e: log.error(f"텔레그램 전송 에러: {e}")

def send_email(subject, html_body, log, md_filename=None, md_content=None):
    if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD: return

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.GMAIL_ADDRESS

    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(html_body, "html"))
    msg.attach(body_part)

    if md_filename and md_content:
        try:
            part = MIMEText(md_content, 'markdown', 'utf-8')
            part.add_header('Content-Disposition', f'attachment; filename="{md_filename}"')
            msg.attach(part)
        except Exception as e:
            log.error(f"마크다운 파일 첨부 실패: {e}")

    # 🛡️ 이메일 전송 3회 재시도
    for attempt in range(3):
        try:
            gmail_host = "smtp.gmail.com"
            with smtplib.SMTP_SSL(gmail_host, 465) as server:
                server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
                server.send_message(msg)
            break
        except Exception as e:
            if attempt == 2:
                log.error(f"이메일 전송 최종 실패: {e}")
            time.sleep(3)

def notify_all(subject, tg_msg, html_body, log, md_filename=None, md_content=None):
    send_telegram(tg_msg, log)
    send_email(subject, html_body, log, md_filename, md_content)
