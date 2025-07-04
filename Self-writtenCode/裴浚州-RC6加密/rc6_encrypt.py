import math
import binascii
import time

#rotate right input x, by n bits
def ROR(x, n, bits = 32):
    mask = (2**n) - 1
    mask_bits = x & mask
    return (x >> n) | (mask_bits << (bits - n))

#rotate left input x, by n bits
def ROL(x, n, bits = 32):
    return ROR(x, bits - n,bits)

#convert input sentence into blocks of binary
#creates 4 blocks of binary each of 32 bits.
def blockConverter(sentence):
    encoded = []
    res = ""
    for i in range(0,len(sentence)):
        if i%4==0 and i!=0 :
            encoded.append(res)
            res = ""
        temp = bin(ord(sentence[i]))[2:]
        if len(temp) <8:
            temp = "0"*(8-len(temp)) + temp
        res = res + temp
    encoded.append(res)
    return encoded

#converts 4 blocks array of long int into string
def deBlocker(blocks):
    s = ""
    for ele in blocks:
        temp =bin(ele)[2:]
        if len(temp) <32:
            temp = "0"*(32-len(temp)) + temp
        for i in range(0,4):
            s=s+chr(int(temp[i*8:(i+1)*8],2))
    return s

#generate key s[0... 2r+3] from given input string userkey
def generateKey(userkey):
    r=12
    w=32
    b=len(userkey)
    modulo = 2**32
    s=(2*r+4)*[0]
    s[0]=0xB7E15163
    for i in range(1,2*r+4):
        s[i]=(s[i-1]+0x9E3779B9)%(2**w)
    encoded = blockConverter(userkey)
    #print encoded
    enlength = len(encoded)
    l = enlength*[0]
    for i in range(1,enlength+1):
        l[enlength-i]=int(encoded[i-1],2)
    
    v = 3*max(enlength,2*r+4)
    A=B=i=j=0
    
    for index in range(0,v):
        A = s[i] = ROL((s[i] + A + B)%modulo,3,32)
        B = l[j] = ROL((l[j] + A + B)%modulo,(A+B)%32,32) 
        i = (i + 1) % (2*r + 4)
        j = (j + 1) % enlength
    return s

def encrypt(sentence,s):
    encoded = blockConverter(sentence)
    enlength = len(encoded)
    A = int(encoded[0],2)
    B = int(encoded[1],2)
    C = int(encoded[2],2)
    D = int(encoded[3],2)
    orgi = []
    orgi.append(A)
    orgi.append(B)
    orgi.append(C)
    orgi.append(D)
    r=12
    w=32
    modulo = 2**32
    lgw = 5
    B = (B + s[0])%modulo
    D = (D + s[1])%modulo 
    start_time = time.time()
    for i in range(1, r + 1):
        t = ROL((B * ((2 * B + 1) % modulo)) % modulo, lgw, 32)
        u = ROL((D * ((2 * D + 1) % modulo)) % modulo, lgw, 32)
        print(f"Round {i}: A={A}, B={B}, C={C}, D={D}, t={t}, u={u}")
        A = (ROL((A ^ t), u % 32, 32) + s[2 * i]) % modulo
        C = (ROL((C ^ u), t % 32, 32) + s[2 * i + 1]) % modulo
        A, B, C, D = B, C, D, A
    print(f"Encryption took {time.time() - start_time:.6f}s")
    cipher = []
    cipher.append(A)
    cipher.append(B)
    cipher.append(C)
    cipher.append(D)
    return orgi,cipher


def main():
    print("ENCRYPTION: ")
    key = input("Enter Key(0-16 characters): ")
    if len(key) <16:
        key = key + " "*(16-len(key))
    key = key[:16]
                         
    print("UserKey: " + key)
    s = generateKey(key)
    sentence = input("Enter Sentence(0-16 characters): ")
    if len(sentence) <16:
        sentence = sentence + " "*(16-len(sentence))
    sentence = sentence[:16]
    
    orgi,cipher = encrypt(sentence,s)
    esentence = deBlocker(cipher)
    
    print("\nInput String: " + sentence)
    print("Original String list: ", orgi)
    
    print("\nEncrypted String list: ", cipher)
    print("Encrypted String: " + binascii.hexlify(esentence.encode()).decode())

if __name__ == "__main__":
    main()