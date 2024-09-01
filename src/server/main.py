import asyncio.subprocess
import socket
from time import asctime
import json
import struct
import os
from module_infos import SERVER_PATH, SAVES_PATH
import asyncio

VALID_REQUEST = 0
WRONG_REQUEST = 1

LOG_FILE = os.path.join(SERVER_PATH, 'server.log')

def write_log(message: str, is_err: bool=False) -> None:
    if is_err:
        message = 'Error: ' + message
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

class Server:
    def __init__(self, host: str, port: int) -> None:
        self.running = True
        self.host = host
        self.port = port
        self.clients: dict[socket.socket, tuple[str, int]] = {}
        write_log(f"launched server at {asctime()}")

    async def run(self) -> None:
        self.server = await asyncio.start_server(self.handle_client, self.host, self.port)
        async with self.server:
            await self.server.serve_forever()

    def close(self) -> None:
        self.server.close()

    def send_json(self, writer: asyncio.StreamWriter, request: dict) -> None:
        request = json.dumps(request).encode()
        message = struct.pack('>I', len(request)) + request
        writer.write(message)
    
    async def receive_msg(self, reader: asyncio.StreamReader) -> dict:
        raw_msglen = await self.recvall(reader, 4)
        if not raw_msglen:
            return {}
        msglen = struct.unpack('>I', raw_msglen)[0]
        message = await self.recvall(reader, msglen)
        if not message:
            return {}
        return json.loads(message)
    
    async def recvall(self, reader: asyncio.StreamReader, size: int) -> bytes:
        msg = b''
        while size:
            new_msg = await reader.read(size)
            if not new_msg:
                return b''
            msg += new_msg
            size -= len(new_msg)
        return msg

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        request = await self.receive_msg(reader)
        if 'method' not in request or not isinstance(request['method'], str):
            write_log(f"Bad request: missing 'method' in {request}")
            self.send_json(writer, {'status': WRONG_REQUEST})
            return
        match request['method'].upper():
            case 'GET':
                self.handle_get(request, writer)
            case value:
                write_log(f"Bad request: wrong value for 'method': {value}")
                self.send_json(writer, {'status': WRONG_REQUEST})

    def handle_get(self, request: dict, writer: asyncio.StreamWriter) -> None:
        if 'wanted-data' not in request:
            write_log(f"Bad request: missing 'wanted-data' in {request}")
            self.send_json(writer, {'status': WRONG_REQUEST})
            return
        match request['wanted-data']:
            case 'saves-list':
                self.send_json(writer, {'status': VALID_REQUEST, 'data': os.listdir(SAVES_PATH)})
            case value:
                write_log(f"Bad request: wrong value for 'method': {value}")
                self.send_json(writer, {'status': WRONG_REQUEST})

try:
    server = Server('127.0.0.1', 12345)
    asyncio.run(server.run())
except Exception as e:
    write_log(repr(e), is_err=True)
