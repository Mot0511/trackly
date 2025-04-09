import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

def send_message(site):
    EMAIL = os.getenv('EMAIL_ADDRESS')
    PASSWORD = os.getenv('EMAIL_PASSWORD')

    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(EMAIL, PASSWORD)
    
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = site.user.email
    msg["Subject"] = f"Обновление на сайте {site.name}"

    text = f'''
        <h1>На странице сайта {site.name} произошло обновление</h1>
        <h2><a href="{site.url}">Перейти на страницу</h2></a>
    '''

    msg.attach(MIMEText(text, "html"))

    smtp_server.sendmail(EMAIL, site.user.email, msg.as_string())