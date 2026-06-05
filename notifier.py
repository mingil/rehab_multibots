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

# 🚀 마크다운 파일명(md_filename)과 내용(md_content) 파라미터를 추가로 받습니다.
def send_email(subject, html_body, md_filename=None, md_content=None):
    if not config.GMAIL_ADDRESS or not config.GMAIL_APP_PASSWORD: return

    # 첨부파일을 넣을 수 있는 'mixed' 타입으로 설정
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.GMAIL_ADDRESS

    # 1. 예쁘게 변환된 HTML 이메일 본문 장착
    body_part = MIMEMultipart("alternative")
    body_part.attach(MIMEText(html_body, "html"))
    msg.attach(body_part)

    # 🚀 2. 옵시디언 마크다운 파일(.md) 첨부 로직 (한글 깨짐 방지를 위해 utf-8 지정)
    if md_filename and md_content:
        try:
            part = MIMEText(md_content, 'markdown', 'utf-8')
            part.add_header('Content-Disposition', f'attachment; filename="{md_filename}"')
            msg.attach(part)
        except Exception as e:
            log.error(f"마크다운 파일 첨부 실패: {e}")

    try:
        gmail_host = "smtp.gmail.com"
        with smtplib.SMTP_SSL(gmail_host, 465) as server:
            server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        log.error(f"이메일 전송 실패: {e}")

def notify_all(subject, tg_msg, html_body, md_filename=None, md_content=None):
    send_telegram(tg_msg)
    # 텔레그램은 HTML만 보내고, 이메일에만 옵시디언 첨부파일을 달아줍니다!
    send_email(subject, html_body, md_filename, md_content)
