import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from telegram import Bot
except ImportError:
    Bot = None  # Telegram não disponível

# --- Configurações ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')

# --- Funções de Comunicação ---
def send_telegram_message(message: str):
    if not Bot or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram não configurado corretamente.")
        return False
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print(f"Mensagem enviada via Telegram: {message}")
        return True
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")
        return False

def send_email(subject: str, message: str):
    if not EMAIL_HOST or not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
        print("E-mail não configurado corretamente.")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        server.quit()
        print(f"E-mail enviado: {subject}")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# --- Função Genérica ---
def notify_user(message: str, subject: str = "Notificação Nexo"):
    telegram_ok = send_telegram_message(message)
    email_ok = send_email(subject, message)
    return telegram_ok or email_ok
