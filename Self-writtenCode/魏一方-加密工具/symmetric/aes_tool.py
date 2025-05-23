from Crypto.Cipher import AES
import base64
import hashlib

class AESCipher:
    # 使用 SHA-256 将任意长度的 key 转换为 32 字节，以适应 AES 的密钥长度要求
    # 这里使用 SHA-256 是因为 AES 支持 128, 192, 256 位密钥长度
    def __init__(self, key: str):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()  

    # PKCS#7 填充
    def _pad(self, text: bytes) -> bytes:
        block_size = AES.block_size
        pad_len = block_size - len(text) % block_size
        return text + bytes([pad_len]) * pad_len

    # 去除 PKCS#7 填充
    def _unpad(self, text: bytes) -> bytes:
        pad_len = text[-1]
        return text[:-pad_len]

    # 使用 AES(CBC 模式) 加密并返回 Base64 字符串
    def encrypt(self, plaintext: str) -> str:
        # 如果明文为空，抛出异常
        if not plaintext:
            raise ValueError("Plaintext is empty")
        cipher = AES.new(self.key, AES.MODE_CBC)
        iv = cipher.iv
        padded_data = self._pad(plaintext.encode('utf-8'))
        ciphertext = cipher.encrypt(padded_data)
        return base64.b64encode(iv + ciphertext).decode('utf-8')

    # 解密 Base64 密文, 先分离 IV, 获取原始明文
    def decrypt(self, ciphertext_b64: str) -> str:
        # 如果密文为空，抛出异常
        if not ciphertext_b64:
            raise ValueError("Ciphertext is empty")
        try:
            raw_data = base64.b64decode(ciphertext_b64)
            iv = raw_data[:AES.block_size]
            enc_bytes = raw_data[AES.block_size:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
            decrypted = self._unpad(cipher.decrypt(enc_bytes))
            return decrypted.decode('utf-8')
        except (ValueError, IndexError, TypeError) as e:
            # 捕获可能在解码或解密时发生的异常，如 Base64 解码失败或索引出错
            raise ValueError("Decryption error: invalid input.") from e

# 测试函数
'''def test_encryption():
    test_key = "bupt"
    test_data = ""
    cipher = AESCipher(test_key)
    enc = cipher.encrypt(test_data)
    dec = cipher.decrypt(enc)
    print("Encrypted:", enc)
    print("Decrypted:", dec)


if __name__ == "__main__":
    test_encryption()'''
