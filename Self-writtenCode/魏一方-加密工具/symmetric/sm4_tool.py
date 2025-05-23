from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from Crypto.Random import get_random_bytes
import base64
import hashlib

class SM4Cipher:
    def __init__(self, key: str):
        # SM4需要16字节，这里用MD5截取16字节
        self.key = hashlib.md5(key.encode('utf-8')).digest()

    # PKCS#7 填充
    # SM4块大小为16字节
    def _pad(self, data: bytes) -> bytes:
        block_size = 16
        pad_len = block_size - len(data) % block_size
        return data + bytes([pad_len]) * pad_len

    # 去除 PKCS#7 填充
    def _unpad(self, data: bytes) -> bytes:
        pad_len = data[-1]
        return data[:-pad_len]

    # 使用 SM4(CBC 模式) 加密并返回 Base64 字符串
    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            raise ValueError("Plaintext is empty")
        iv = get_random_bytes(16)
        crypt_sm4 = CryptSM4()
        crypt_sm4.set_key(self.key, SM4_ENCRYPT)
        enc = crypt_sm4.crypt_cbc(iv, self._pad(plaintext.encode('utf-8')))
        return base64.b64encode(iv + enc).decode('utf-8')

    # 解密 Base64 密文, 先分离 IV, 获取原始明文
    def decrypt(self, ciphertext_b64: str) -> str:
        if not ciphertext_b64:
            raise ValueError("Ciphertext is empty")
        try:
            raw_data = base64.b64decode(ciphertext_b64)
            iv = raw_data[:16]
            enc = raw_data[16:]
            crypt_sm4 = CryptSM4()
            crypt_sm4.set_key(self.key, SM4_DECRYPT)
            dec = crypt_sm4.crypt_cbc(iv, enc)
            return self._unpad(dec).decode('utf-8')
        except (ValueError, IndexError, TypeError) as e:
            raise ValueError("Decryption error: invalid input.") from e

#测试函数
'''def test_sm4():
    test_key = "key"
    test_data = "PvJ3TWeFnjlz9lsTacIjpy85dBjo/xx6xyse4zS+pnaAeBoHTOKS+QiJYAHjWsWA"
    cipher = SM4Cipher(test_key)
    enc = cipher.encrypt(test_data)
    dec = cipher.decrypt(enc)
    print("Encrypted:", enc)
    print("Decrypted:", dec)

if __name__ == "__main__":
    test_sm4()'''