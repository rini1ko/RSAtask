import socket
import threading
import json
import my_rsa
import hashlib
import random
import string

def xor_cipher(text, key):
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))
def generate_secret(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
class Server:

    def __init__(self, port: int) -> None:
        self.host = '127.0.0.1'
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.secret_key = generate_secret()
    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(100)
        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")

            pub_key_data = c.recv(1024).decode()
            client_public_key = json.loads(pub_key_data)

            # encrypt the secret with the clients public key

            encrypted_secret = my_rsa.encrypt(client_public_key, self.secret_key)

            # send the encrypted secret to a client 

            c.send(json.dumps(encrypted_secret).encode())

            self.broadcast(f'new person has joined: {username}')
            self.username_lookup[c] = username
            self.clients.append(c)
            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    def broadcast(self, msg: str):
        # encrypt the message

        msg_hash = hashlib.sha256(msg.encode()).hexdigest()

        encrypted_msg = xor_cipher(msg, self.secret_key)

        msg_to_send = json.dumps({"hash": msg_hash, "msg": encrypted_msg})

        for client in self.clients: 
            client.send(msg_to_send.encode())

    def handle_client(self, c: socket, addr):
        while True:
            msg = c.recv(1024)
            # print(f"[msg sent]: {msg.decode()}")
            for client in self.clients:
                if client != c:
                    client.send(msg)

if __name__ == "__main__":
    s = Server(9001)
    s.start()