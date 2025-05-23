from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

class RSA1024:

    def __init__(self, private_key: str = None, public_key: str = None):
        try:
            if private_key:
                self.key = RSA.import_key(private_key)  # 导入用户提供的私钥
                self.public_key = self.key.publickey()  # 获取公钥
            elif public_key:
                self.public_key = RSA.import_key(public_key)  # 导入用户提供的公钥
            else:
                raise ValueError("Either private key or public key must be provided")
        except Exception as e:
            raise RuntimeError("RSA key initialization error occurred") from e

    @staticmethod
    def create_key_pair() -> tuple:
        """
        创建新的 RSA 密钥对
        :return: (私钥字符串, 公钥字符串)
        """
        key = RSA.generate(1024)
        private_key = key.export_key(format='PEM').decode('utf-8')
        public_key = key.publickey().export_key(format='PEM').decode('utf-8')
        return private_key.strip(), public_key.strip()  # 确保去除多余的空白字符

    def encrypt(self, plaintext: str) -> bytes:
        """
        :param plaintext: 要加密的明文字符串
        :return: 加密后的字节数据
        :raises ValueError: 如果明文为空
        :raises RuntimeError: 如果加密过程中发生错误
        """
        if not plaintext:
            raise ValueError("Plaintext is empty")
        try:
            cipher = PKCS1_OAEP.new(self.public_key)  # 使用公钥初始化加密器
            return cipher.encrypt(plaintext.encode('utf-8'))  
        except Exception as e:
            raise RuntimeError("RSA encryption error occurred") from e

    def decrypt(self, ciphertext: bytes) -> str:
        """
        :param ciphertext: 要解密的密文字节数据
        :return: 解密后的明文字符串
        :raises ValueError: 如果密文为空
        :raises RuntimeError: 如果解密过程中发生错误
        """
        if not ciphertext:
            raise ValueError("Ciphertext is empty")
        try:
            cipher = PKCS1_OAEP.new(self.key)  # 使用私钥初始化解密器
            return cipher.decrypt(ciphertext).decode('utf-8')  
        except Exception as e:
            raise RuntimeError("RSA decryption error occurred") from e

    def sign(self, message: str) -> bytes:
        """
        :param message: 要签名的消息字符串
        :return: 签名后的字节数据
        :raises ValueError: 如果消息为空
        :raises RuntimeError: 如果签名过程中发生错误
        """
        if not message:
            raise ValueError("Message is empty")
        try:
            from Crypto.Signature import pkcs1_15
            from Crypto.Hash import SHA256
            h = SHA256.new(message.encode('utf-8'))  # 计算消息的 SHA256 哈希值
            return pkcs1_15.new(self.key).sign(h)  # 使用私钥对哈希值进行签名
        except Exception as e:
            raise RuntimeError("RSA signing error occurred") from e

    def verify(self, message: str, signature_hex: str) -> bool:
        """
        验证签名
        :param message: 原始消息字符串
        :param signature_hex: 签名的十六进制字符串
        :return: 验证结果，True 表示验证成功，False 表示验证失败
        """
        if not message or not signature_hex:
            raise ValueError("Message or signature is empty")
        try:
            signature = bytes.fromhex(signature_hex)  # 将十六进制字符串转换为字节
            from Crypto.Signature import pkcs1_15
            from Crypto.Hash import SHA256
            h = SHA256.new(message.encode('utf-8'))
            pkcs1_15.new(self.public_key).verify(h, signature)
            return True
        except Exception:
            return False
