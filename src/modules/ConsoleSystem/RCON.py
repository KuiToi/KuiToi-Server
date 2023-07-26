import hashlib
import os
from base64 import b64decode, b64encode

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from core import get_logger

"""
shared key: SHA256 of "password"
<header>: "\x00\x00\x00\x00" (Byte order: Little Endian) - like you use
<iv>: A set of random bytes packed in base64 (New for each message)
-> To server
<- From server

Open TCP connection /
|  -> "<iv>:hello" Without header, immediately with AES encryption (shared key)
|  *Decrypt and some processes*
|  Fail /
|    |  <- ":E:Bad key" | ":E:Error Message" Without header, without AES encryption
|    |  tcp.close()  # End
|  Success /
|    |  <- "<iv>:hello" with header, with AES encryption
|    |  (Next, everywhere with header, with AES encryption)
|  -> "<iv>:<header>Cs:ver" 
|  <- "<iv>:<header>Os:KuiToi 0.4.3 | "<iv>:<header>Os:BeamMP 3.2.0"
|  # Prints server and they version
|  -> "<iv>:<header>Cs:commands" 
|  <- "<iv>:<header>Os:stop,help,plugins" | "<iv>:<header>Os:SKIP" For an autocomplete; "SKIP" For no autocomplete;
|  *Ready to handle commands*
|  -> "<iv>:<header>C:help" 
|  <- "<iv>:<header>O:stop: very cool stop\nhelp: Yayayayoy"
|  -> "<iv>:<header>C:...." 
|  <- "<iv>:<header>O:...."
|  -> "<iv>:<header>C:exit" 
|  tcp.close()

Codes: 
* "hello" - Hello message
* "E:error_message" - Send RCON error
* "C:command" - Receive command
* "Cs:" - Receive system command
* "O:output" - Send command output
* "Os:" - Send system output

"""


class RCONSystem:
    console = None

    def __init__(self, key, host, port):
        self.log = get_logger("RCON")
        self.key = key
        self.host = host
        self.port = port

    def encrypt(self, message, key):
        self.log.debug(f"Encrypt message: {message}")
        key = hashlib.sha256(key).digest()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.encode('utf-8')) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        encoded_data = b64encode(encrypted_data)
        encoded_iv = b64encode(iv)
        return encoded_iv + b":" + encoded_data

    def decrypt(self, ciphertext, key):
        self.log.debug(f"Dencrypt message: {ciphertext}")
        key = hashlib.sha256(key).digest()
        encoded_iv, encoded_data = ciphertext.split(":")
        iv = b64decode(encoded_iv)
        encrypted_data = b64decode(encoded_data)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data.decode('utf-8')

    async def handle_client(self):
        pass

    async def start(self):
        self.log.info("TODO: RCON")

    async def stop(self):
        pass
