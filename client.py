import socket
import threading
from sympy import randprime
import my_rsa
import json
import hashlib
import time
def xor_cipher(text, key):
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))
class Client:
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username
        self.private_key =None
        self.secret_key = None
    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())
        time.sleep(0.2)

        p=randprime(100, 1000)
        q=randprime(100, 1000)

        public_key, private_key = my_rsa.generate_keypair(p, q)
        self.private_key=private_key
        # exchange public keys
        pub_key_json = json.dumps(public_key)
        self.s.send(pub_key_json.encode())
        # receive the encrypted secret key
        encrypted_secret_data = self.s.recv(1024).decode()
        encrypted_secret = json.loads(encrypted_secret_data)

        self.secret_key = my_rsa.decrypt(self.private_key, encrypted_secret)

        message_handler = threading.Thread(target=self.read_handler,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler,args=())
        input_handler.start()
    def read_handler(self):
        while True:
            message = self.s.recv(1024).decode()

            # decrypt message with the secrete key

            if not message:
                    break

            msg_to_send = json.loads(message)
            received_hash = msg_to_send["hash"]
            encrypted_msg = msg_to_send["msg"]

            decrypted_msg = xor_cipher(encrypted_msg, self.secret_key)

            calculated_hash = hashlib.sha256(decrypted_msg.encode()).hexdigest()

            if calculated_hash == received_hash:
                print(decrypted_msg)

    def write_handler(self):
        while True:
            message = input()

            formatted_msg = f"{self.username}: {message}"

            msg_hash = hashlib.sha256(formatted_msg.encode()).hexdigest()

            encrypted_msg = xor_cipher(formatted_msg, self.secret_key)

            msg_to_send = json.dumps({"hash": msg_hash, "msg": encrypted_msg})
            self.s.send(msg_to_send.encode())

if __name__ == "__main__":
    name = input("Enter your name: ")
    cl = Client("127.0.0.1", 9001, name)
    cl.init_connection()