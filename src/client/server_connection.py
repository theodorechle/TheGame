import subprocess
import socket
import struct
import json
import sys
import os
from module_infos import SERVER_PATH

class ServerConnection:
    VALID_REQUEST = 0
    WRONG_REQUEST = 1
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_process = subprocess.Popen(
            [sys.executable, os.path.join(SERVER_PATH, 'main.py')],
            stdout=sys.stdout,
            stderr=sys.stderr,
            start_new_session=True)
        self.server_socket = self.connect_to_server()

    def stop(self) -> None:
        self.server_process.kill()

    def connect_to_server(self) -> socket.socket:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        return client_socket

    def send_json(self, request: dict) -> dict|None:
        request = json.dumps(request).encode()
        message = struct.pack('>I', len(request)) + request
        self.server_socket.sendall(message)
        return self.receive_msg()
    
    def receive_msg(self, ) -> dict:
        raw_msglen = self.recvall(4)
        if not raw_msglen:
            return {}
        msglen = struct.unpack('>I', raw_msglen)[0]
        message = self.recvall(msglen)
        if not message:
            return {}
        return json.loads(message)
    
    
    def recvall(self, size: int) -> bytes:
        msg = b''
        while size:
            new_msg = self.server_socket.recv(size)
            if not new_msg:
                return b''
            msg += new_msg
            size -= len(new_msg)
        return msg