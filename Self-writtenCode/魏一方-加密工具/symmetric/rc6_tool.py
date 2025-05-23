import base64
import struct
import hashlib

BLOCK_SIZE = 16
ROUNDS = 20

class RC6Cipher:
    def __init__(self, key: str):
        # 将字符串密钥编码为字节后进行 SHA-256 哈希处理，生成固定长度的密钥
        self.key = hashlib.sha256(key.encode('utf-8')).digest()
        self._sub_keys = self._key_schedule(self.key)

    def _key_schedule(self, key: bytes):
        return [0] * (2 * ROUNDS + 4)

    def _pad(self, data: bytes) -> bytes:
        pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
        return data + bytes([pad_len]) * pad_len

    def _unpad(self, data: bytes) -> bytes:
        pad_len = data[-1]
        return data[:-pad_len]

    def _encrypt_block(self, block: bytes) -> bytes:
        # 采用 RC6 每轮的旋转及子密钥操作进行分块加密
        A, B, C, D = struct.unpack("<4I", block)
        B = (B + self._sub_keys[0]) & 0xffffffff
        D = (D + self._sub_keys[1]) & 0xffffffff
        for i in range(1, ROUNDS + 1):
            t = (B * ((2 * B) + 1)) & 0xffffffff
            t = ((t << 5) | (t >> (32 - 5))) & 0xffffffff
            u = (D * ((2 * D) + 1)) & 0xffffffff
            u = ((u << 5) | (u >> (32 - 5))) & 0xffffffff
            A ^= t
            A = (A << (u & 31) | A >> (32 - (u & 31))) & 0xffffffff
            A = (A + self._sub_keys[2 * i]) & 0xffffffff
            C ^= u
            C = (C << (t & 31) | C >> (32 - (t & 31))) & 0xffffffff
            C = (C + self._sub_keys[2 * i + 1]) & 0xffffffff
            A, B, C, D = B, A, D, C
        A, B, C, D = B, A, D, C
        B = (B + self._sub_keys[2 * ROUNDS + 2]) & 0xffffffff
        D = (D + self._sub_keys[2 * ROUNDS + 3]) & 0xffffffff
        return struct.pack("<4I", A, B, C, D)

    def _decrypt_block(self, block: bytes) -> bytes:
        # 对加密块执行逆操作, 还原明文块
        A, B, C, D = struct.unpack("<4I", block)
        B = (B - self._sub_keys[2 * ROUNDS + 2]) & 0xffffffff
        D = (D - self._sub_keys[2 * ROUNDS + 3]) & 0xffffffff
        A, B, C, D = B, A, D, C
        for i in range(ROUNDS, 0, -1):
            A, B, C, D = B, A, D, C
            u = (D * ((2 * D) + 1)) & 0xffffffff
            u = ((u << 5) | (u >> (32 - 5))) & 0xffffffff
            t = (B * ((2 * B) + 1)) & 0xffffffff
            t = ((t << 5) | (t >> (32 - 5))) & 0xffffffff
            C = (C - self._sub_keys[2 * i + 1]) & 0xffffffff
            C = (C >> (t & 31) | C << (32 - (t & 31))) & 0xffffffff
            C ^= u
            A = (A - self._sub_keys[2 * i]) & 0xffffffff
            A = (A >> (u & 31) | A << (32 - (u & 31))) & 0xffffffff
            A ^= t
        B = (B - self._sub_keys[0]) & 0xffffffff
        D = (D - self._sub_keys[1]) & 0xffffffff
        return struct.pack("<4I", A, B, C, D)

    def encrypt(self, plaintext: str) -> str:
        # 先对明文进行填充, 分块加密后再使用 Base64 编码
        if not plaintext:
            raise ValueError("Plaintext is empty.")
        data = self._pad(plaintext.encode('utf-8'))
        blocks = []
        for i in range(0, len(data), BLOCK_SIZE):
            block_part = data[i:i+BLOCK_SIZE]
            blocks.append(self._encrypt_block(block_part))
        encrypted_data = b''.join(blocks)
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt(self, ciphertext_b64: str) -> str:
        # 先做 Base64 解码, 再分块解密并去除填充
        if not ciphertext_b64:
            raise ValueError("Ciphertext is empty.")
        try:
            raw_data = base64.b64decode(ciphertext_b64)
            blocks = []
            for i in range(0, len(raw_data), BLOCK_SIZE):
                block_part = raw_data[i:i+BLOCK_SIZE]
                blocks.append(self._decrypt_block(block_part))
            decrypted = b''.join(blocks)
            return self._unpad(decrypted).decode('utf-8')
        except (ValueError, IndexError, TypeError) as e:
            raise ValueError("Decryption error: invalid input.") from e

#测试函数
'''def test_rc6_cipher():
    key = "testkey123"  
    plaintext = "aadsdadsa message."
    cipher = RC6Cipher(key)

    print("Original plaintext:", plaintext)

    encrypted = cipher.encrypt(plaintext)
    print("Encrypted ciphertext:", encrypted)

    decrypted = cipher.decrypt(encrypted)
    print("Decrypted plaintext:", decrypted)


if __name__ == "__main__":
    test_rc6_cipher()'''
