from Crypto.PublicKey import ECC 
from Crypto.Signature import DSS  
from Crypto.Hash import SHA256  

class ECDSA:

    def __init__(self, private_key: str = None, public_key: str = None):
        try:
            if private_key:
                self.key = ECC.import_key(private_key)  # 导入用户提供的私钥
                self.public_key = self.key.public_key()  # 获取公钥
            elif public_key:
                self.public_key = ECC.import_key(public_key)  # 导入用户提供的公钥
            else:
                raise ValueError("Either private key or public key must be provided")
        except Exception as e:
            raise RuntimeError("ECDSA key initialization error occurred") from e 

    @staticmethod
    def create_key_pair() -> tuple:
        """
        创建新的 ECDSA 密钥对
        :return: (私钥字符串, 公钥字符串)
        """
        key = ECC.generate(curve='P-256')
        private_key = key.export_key(format='PEM')
        public_key = key.public_key().export_key(format='PEM')
        return private_key.strip(), public_key.strip()  # 确保去除多余的空白字符

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
            h = SHA256.new(message.encode('utf-8'))  # 计算消息的 SHA256 哈希值
            signer = DSS.new(self.key, 'fips-186-3')  # 初始化 DSS 签名器
            return signer.sign(h)  # 使用私钥对哈希值进行签名
        except Exception as e:
            raise RuntimeError("ECDSA signing error occurred") from e  

    def verify(self, message: str, signature: bytes) -> bool:
        """
        :param message: 原始消息字符串
        :param signature: 签名的字节数据
        :return: 验证结果，True 表示验证成功，False 表示验证失败
        :raises ValueError: 如果消息或签名为空
        """
        if not message or not signature:
            raise ValueError("Message or signature is empty")  
        try:
            h = SHA256.new(message.encode('utf-8'))  # 计算消息的 SHA256 哈希值
            verifier = DSS.new(self.public_key, 'fips-186-3')  
            verifier.verify(h, signature)  # 验证签名
            return True  
        except Exception:
            return False

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
            h = SHA256.new(message.encode('utf-8'))
            verifier = DSS.new(self.public_key, 'fips-186-3')
            verifier.verify(h, signature)
            return True
        except Exception:
            return False
