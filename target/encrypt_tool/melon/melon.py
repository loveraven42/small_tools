# -*- coding:utf-8 -*-
# encrypt/decrypt to dat 
# date:2013-4-10 by liuyongming

from Crypto.Cipher import ARC4
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA
from Crypto import Random
import os, sys
import getopt
import random
import string

key_seed = '0987654321abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-=_+'
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'), ord('A')+6)]

base_dir = os.path.dirname(__file__)


def pkcs1_v1_5():
    f = open('rsa.pub', 'r')
    key1 = RSA.importKey(f.read())
    message = 'To be encrypted'
    h = SHA.new(message)

    cipher = PKCS1_v1_5.new(key1)
    ciphertext = cipher.encrypt(message+h.digest())

    key2=RSA.importKey(f.read())

    dsize = SHA.digest_size
    sentinel = Random.new().read(15+dsize)

    cipher = PKCS1_v1_5.new(key2)
    message = cipher.decrypt(ciphertext, sentinel)
    digest = SHA.new(message[:-dsize]).digest()
    if digest == message[-dsize:]:
        print message
        print "OK"
    else:
        print "NO"


class RSACipher():
    # test for PKCS1_v1_5 签名
    def get_rsakey(self, rsa_priv, rsa_pub):    
        key = RSA.generate(4096)

        fpriv = open(rsa_priv, 'w')
        fpriv.write(key.exportKey('PEM'))
        fpriv.close()

        fpub = open(rsa_pub, 'w')
        fpub.write(key.exportKey('DER'))
        fpub.close()

    def get_key(self, key_path):
        try:
            key = RSA.importKey(open(key_path).read())
            self.key = key
        except Exception, e:
            self.key = None


    # test for PKCS1_OAEP 加解密字符串
    def pkcs1_oaep(self, rsa_priv, rsa_pub):
        key_priv = self.get_privkey(rsa_priv)
        key_pub = self.get_pubkey(rsa_pub)
        message = 'LDqW3+hw2SNzHba)7Gsi*-F6XnPT(&Zjc%r54#k0Y=UQ^BO1vJIgyxoMe8t$'
        print "plaintext: ", message

        cipher_priv = PKCS1_OAEP.new(key_priv)
        ciphertext = cipher_priv.encrypt(message)
        print 'encrypt text: ',ciphertext

        cipher_pub = PKCS1_OAEP.new(key_pub)
        messages = cipher_pub.decrypt(ciphertext)
        print "decrypt text: ", messages

    def get_keysize(self, key_path):
        try:
            self.get_key(key_path)
            return self.key.size()
        except Exception, e:
            return None

    def encrypt(self, plaintext):
        cipher = PKCS1_OAEP.new(self.key)
        try:
            ciphertext = cipher.encrypt(plaintext)
            return ciphertext
        except Exception, e:
            return None

    def decrypt(self, ciphertext):
        cipher = PKCS1_OAEP.new(self.key)
        try:
            plaintext = cipher.decrypt(ciphertext)
            return plaintext
        except Exception, e:
            return None


# 十六进制转十进制
def hextodec(string_num):
    return str(int(string_num.upper(), 16))

# 十进制转十六进制
def dectohex(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0:
            break
        num, rem = divmod(num, 16)
        mid.append(base[rem])
    
    return ''.join([str(x) for x in mid[::-1]])


def encrypt(source_file, dest_file):
    fin = open(source_file, 'rb')
    fin.seek(0, 2)
    fin.seek(0, 0)
    num = 192
    count = 64
    i = 0
    times = int(num/64)
    key = ''
    while i != times:
        key = string.join(random.sample(key_seed, count)).replace(' ', '')
        i += 1

    cipher = ARC4.new(key)

    Cipher = RSACipher()
    key_path = os.path.join(base_dir, 'rsa.priv')
    if not os.path.exists(key_path):
        return 1
    else:
        Cipher.get_key(key_path)

    fout = open(dest_file, 'wb')

    while True:
        data = fin.read(65520)
        length = len(data)
        if not data:
            break
        en_data = cipher.encrypt(data)
        fout.write(en_data)
    
    # 处理RC4的密钥
    cipherText = Cipher.encrypt(key)

    fout.write(cipherText)

    # 随机填充若干字节数据
    num = random.randint(100,255)
    count = 64
    i = 0
    times = int(num/64)
    rand_str = ''
    while i != times:
        rand_str += string.join(random.sample(key_seed, count)).replace(' ', '')
        i += 1
    sum = count*times
    left = num - sum
    rand_str += string.join(random.sample(key_seed, left)).replace(' ', '')
        
    hex_num = dectohex(num)
    rand_cipher = cipher.encrypt(rand_str)
    
    # 将随机字符的密文写入文件结尾
    fout.write(rand_cipher)

    # rsa加密随机字符的个数
    hex_cipher = Cipher.encrypt(hex_num)

    fout.write(hex_cipher)
    
    fin.close()
    fout.close()
    return 0


def decrypt(source_file, dest_file):
    global pub
    fin = open(source_file, 'rb')
    fin.seek(0, 2)
    file_len = fin.tell()

    Cipher = RSACipher()    

    fin.seek(file_len-512, 0)
    hex_cipher = fin.read(512)

    rsa_file = os.path.join(base_dir, 'rsa.pub')
    if not os.path.exists(rsa_file):
        return 1
    else:
        Cipher.get_key(rsa_file)
        hex_num = Cipher.decrypt(hex_cipher)
        if hex_num == None:
            return 2

    num = int(hextodec(hex_num))

    count_rand = num + 512 + 512
    fin.seek(file_len-count_rand, 0)
    cipherText = fin.read(512)
    
    key = Cipher.decrypt(cipherText)
    
    cipher = ARC4.new(key)

    fout = open(dest_file, 'wb')

    fin.seek(0, 0)
    while True:
        data = fin.read(65520)
        if not data:
            break
        de_data = cipher.decrypt(data)
        fout.write(de_data)
    # 裁剪部分    
    fout.truncate(file_len-count_rand)

    fin.close()
    fout.close()
    return 0

if __name__ == '__main__':
    mode = sys.argv[1]
    src_file = sys.argv[2]
    dst_file = sys.argv[3]
    if mode == 'encrypt':
        print encrypt(src_file, dst_file)
    elif mode == 'decrypt':
        print decrypt(src_file, dst_file)
    else:
        print '5'

