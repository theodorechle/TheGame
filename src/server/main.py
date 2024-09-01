"""
Messages sent to the server must follow this template:
{
    'method': 'GET|DELETE',
    'data': {
        'type': Any,
        ...
    },
    ...
}

Messages sent by the server must follow this template:
{
    'status': int,
    'data': {
        ...
    },
    ...
}
"""

import asyncio.subprocess
import socket
from time import asctime
import json
import struct
import os
from module_infos import SERVER_PATH, SAVES_PATH
import asyncio

LOG_FILE = os.path.join(SERVER_PATH, 'server.log')

def write_log(message: str, is_err: bool=False) -> None:
    if is_err:
        message = 'Error: ' + message
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

class Server:
    VALID_REQUEST = 0
    WRONG_REQUEST = 1
    def __init__(self, host: str, port: int) -> None:
        self.running = True
        self.host = host
        self.port = port
        self.clients: dict[socket.socket, tuple[str, int]] = {}
        write_log(f"launched server at {asctime()}")

    async def run(self) -> None:
        self.server = await asyncio.start_server(self.handle_client_request, self.host, self.port)
        async with self.server:
            await self.server.serve_forever()

    def close(self) -> None:
        self.server.close()

    async def send_json(self, writer: asyncio.StreamWriter, request: dict) -> None:
        request = json.dumps(request).encode()
        message = struct.pack('>I', len(request)) + request
        writer.write(message)
        await writer.drain()

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

    async def handle_client_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        try:
            while True:
                request = await self.receive_msg(reader)
                if not request:
                    write_log(f"Client {addr} disconnected")
                    break
                write_log(f"Client {addr} sent request {request}")
                if 'method' not in request or not isinstance(request['method'], str):
                    write_log(f"Bad request: missing 'method' in {request}")
                    await self.send_json(writer, {'status': self.WRONG_REQUEST})
                    return
                match request['method'].upper():
                    case 'GET':
                        await self.handle_get(request, writer)
                    case 'DELETE':
                        await self.handle_delete(request, writer)
                    case value: # treat as an error
                        write_log(f"Bad request: wrong value for 'method': {value}")
                        await self.send_json(writer, {'status': self.WRONG_REQUEST})
        except Exception as e:
            write_log(f'Error handling client {addr}: {repr(e)}', is_err=True)
        finally:
            writer.close()
            await writer.wait_closed()
            write_log(f"Connection closed for client {addr}")

    async def get_data(self, request: dict, writer: asyncio.StreamWriter) -> dict|None:
        if not isinstance(request.get('data', None), dict):
            write_log(f"Bad request: missing 'data' in {request}")
            await self.send_json(writer, {'status': self.WRONG_REQUEST})
            return
        data = request['data']
        if 'type' not in data:
            write_log(f"Bad request: missing 'type' in data {data}")
            await self.send_json(writer, {'status': self.WRONG_REQUEST})
            return
        return data

    async def handle_get(self, request: dict, writer: asyncio.StreamWriter) -> None:
        data: dict|None = await self.get_data(request, writer)
        if data is None: return
        match request['data']['type']:
            case 'saves-list':
                await self.send_json(writer, {'status': self.VALID_REQUEST, 'data': os.listdir(SAVES_PATH)})
            case value:
                write_log(f"Bad request: wrong value for data type: '{value}'")
                await self.send_json(writer, {'status': self.WRONG_REQUEST})

    async def handle_delete(self, request: dict, writer: asyncio.StreamWriter) -> None:
        data: dict|None = await self.get_data(request, writer)
        if data is None: return
        match request['data']['type']:
            case 'save':
                dir_name = request['data'].get('value', None)
                if dir_name is None:
                    return
                dir_name = os.path.join(SAVES_PATH, dir_name)
                if os.path.isdir(dir_name):
                    delete_folder(dir_name)
                    await self.send_json(writer, {'status': self.VALID_REQUEST})
            case value:
                write_log(f"Bad request: wrong value for data type: '{value}'")
                await self.send_json(writer, {'status': self.WRONG_REQUEST})

def delete_folder(path) -> None:
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            delete_folder(file_path)
        else:
            os.remove(file_path)
    os.rmdir(path)


try:
    server = Server('127.0.0.1', 12345)
    asyncio.run(server.run())
except Exception as e:
    write_log(repr(e), is_err=True)
