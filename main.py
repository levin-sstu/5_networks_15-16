import socket
import ssl
import base64
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import json


# Функция для подключения к SMTP серверу через SSL
def connect_smtp_server(host, port, username, password):
    context = ssl.create_default_context()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = context.wrap_socket(server, server_hostname=host)
    server.connect((host, port))
    server.sendall(f"EHLO {host}\r\n".encode())
    server.sendall(f"AUTH LOGIN\r\n".encode())
    server.sendall(base64.b64encode(username.encode()) + b"\r\n")
    server.sendall(base64.b64encode(password.encode()) + b"\r\n")
    return server


# Функция для отправки письма
def send_email(server, from_email, to_email, subject, body, attachment_path=None):
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Прикрепляем файл
    if attachment_path:
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={filename}')
        message.attach(part)

    # Отправляем письмо
    server.sendall(f"MAIL FROM:<{from_email}>\r\n".encode())
    server.sendall(f"RCPT TO:<{to_email}>\r\n".encode())
    server.sendall(b"DATA\r\n")
    server.sendall(message.as_string().encode())
    server.sendall(b"\r\n.\r\n")
    server.sendall(b"QUIT\r\n")


# Основная логика программы
def main():
    with open('recipients.json') as f:
        data = json.load(f)

    smtp_host = 'smtp.mail.ru'
    smtp_port = 465
    smtp_username = ''
    smtp_password = ''

    # Подключаемся к серверу
    server = connect_smtp_server(smtp_host, smtp_port, smtp_username, smtp_password)

    for recipient in data['recipients']:
        to_email = recipient['email']
        subject = 'Индивидуальное сообщение'
        body = f"Привет, {recipient['name']}!\n\nЭто ваше индивидуальное сообщение."
        attachment_path = recipient['file']

        # Отправляем индивидуальное письмо
        send_email(server, smtp_username, to_email, subject, body, attachment_path)

    server.close()


if __name__ == "__main__":
    main()
