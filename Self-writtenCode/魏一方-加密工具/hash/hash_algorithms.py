import hashlib
import hmac
from hashlib import pbkdf2_hmac

class SHA1Hash:
    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            hasher = hashlib.sha1()
            hasher.update(data.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            raise RuntimeError("SHA1 hashing error occurred") from e


class SHA256Hash:
    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            hasher = hashlib.sha256()
            hasher.update(data.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            raise RuntimeError("SHA256 hashing error occurred") from e


class SHA3_256Hash:
    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            hasher = hashlib.sha3_256()
            hasher.update(data.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            raise RuntimeError("SHA3-256 hashing error occurred") from e


class RIPEMD160Hash:
    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            hasher = hashlib.new('ripemd160')
            hasher.update(data.encode('utf-8'))
            return hasher.hexdigest()
        except Exception as e:
            raise RuntimeError("RIPEMD160 hashing error occurred") from e


class HMacSHA1:
    def __init__(self, key: str):
        if not key:
            raise ValueError("Key is empty")
        self.key = key.encode('utf-8')

    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            return hmac.new(self.key, data.encode('utf-8'), hashlib.sha1).hexdigest()
        except Exception as e:
            raise RuntimeError("HMacSHA1 hashing error occurred") from e


class HMacSHA256:
    def __init__(self, key: str):
        if not key:
            raise ValueError("Key is empty")
        self.key = key.encode('utf-8')

    def hash(self, data: str) -> str:
        if not data:
            raise ValueError("Input data is empty")
        try:
            return hmac.new(self.key, data.encode('utf-8'), hashlib.sha256).hexdigest()
        except Exception as e:
            raise RuntimeError("HMacSHA256 hashing error occurred") from e


class PBKDF2:
    def __init__(self, key: str, salt: str, iterations: int):
        if not key or not salt:
            raise ValueError("Key or salt is empty")
        self.key = key.encode('utf-8')
        self.salt = salt.encode('utf-8')
        self.iterations = iterations

    def hash(self, dklen: int = 32) -> str:  
        try:
            return pbkdf2_hmac('sha256', self.key, self.salt, self.iterations, dklen).hex()
        except Exception as e:
            raise RuntimeError("PBKDF2 hashing error occurred") from e


# 测试函数
'''def test_hash_algorithms():
    try:
        sha1 = SHA1Hash()
        print("SHA1:", sha1.hash("test"))

        sha256 = SHA256Hash()
        print("SHA256:", sha256.hash("test"))

        sha3 = SHA3_256Hash()
        print("SHA3-256:", sha3.hash("test"))

        ripemd160 = RIPEMD160Hash()
        print("RIPEMD160:", ripemd160.hash("test"))

        hmac_sha1 = HMacSHA1("secret")
        print("HMacSHA1:", hmac_sha1.hash("test"))

        hmac_sha256 = HMacSHA256("secret")
        print("HMacSHA256:", hmac_sha256.hash("test"))

        pbkdf2 = PBKDF2("password", "salt", 100000)
        print("PBKDF2:", pbkdf2.hash(64))
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    test_hash_algorithms()'''
