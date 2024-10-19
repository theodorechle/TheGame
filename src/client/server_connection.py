import subprocess
import asyncio
import struct
import json
import sys
import os
from module_infos import SERVER_PATH
from logs import write_log
from typing import Any

class ServerConnection:
    VALID_REQUEST = 1
    WRONG_REQUEST = 0
    TIME_BEFORE_CANCELLING_CONNECTION_S = 1
    NB_CONNECTIONS_ATTEMPTS = 5
    TIME_BEFORE_NEW_CONNECTION_ATTEMPT_S = 1
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.server_process: subprocess.Popen[bytes]|None = None
    
    def launch_local_server(self) -> None:
        if self.server_process is not None: return
        self.server_process = subprocess.Popen(
            [sys.executable, os.path.join(SERVER_PATH, 'main.py')],
            stdout=sys.stdout,
            stderr=sys.stderr,
            start_new_session=True)
        write_log("Created local server")
        

    def local_server_exists(self) -> bool:
        return self.server_process is not None
    
    def stop_local_server(self) -> None:
        if self.server_process is None: return
        self.server_process.kill()
        self.server_process = None
        write_log("Closed local server")

    async def stop(self) -> None:
        if self.writer is None: return
        self.writer.close()
        await self.writer.wait_closed()

    async def start(self) -> None:
        write_log(f"Joining server at {self.host}:{self.port}")
        for nb_attempts in range(self.NB_CONNECTIONS_ATTEMPTS):
            try:
                self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=self.TIME_BEFORE_CANCELLING_CONNECTION_S)
            except (asyncio.TimeoutError, ConnectionError):
                write_log(f"Failed to connect to server at {self.host}:{self.port} (attempt {nb_attempts + 1})", True)
                if nb_attempts == self.NB_CONNECTIONS_ATTEMPTS:
                    write_log("Failed to join the server (waited to long)", True)
                    raise ConnectionError
                await asyncio.sleep(self.TIME_BEFORE_NEW_CONNECTION_ATTEMPT_S)
        if self.reader is None or self.writer is None:
            write_log(f"Connection error; reader: {self.reader}, writer: {self.writer}", True)
            raise ConnectionError

    async def send_json(self, request: dict[str, Any]) -> None:
        if self.writer is None: return
        json_request = json.dumps(request)
        write_log(f"Sending {request}")
        bytes_request = json_request.encode()
        message = struct.pack('>I', len(bytes_request)) + bytes_request
        self.writer.write(message)
        await self.writer.drain()
    
    async def receive_msg(self, ) -> dict[str, Any]:
        raw_msglen = await self.recvall(4)
        if not raw_msglen:
            return {}
        msglen = struct.unpack('>I', raw_msglen)[0]
        message = await self.recvall(msglen)
        if not message:
            return {}
        return json.loads(message)    
    
    async def recvall(self, size: int) -> bytes:
        if self.reader is None: return b''
        msg = b''
        while size:
            new_msg = await self.reader.readexactly(size)
            if not new_msg:
                return b''
            msg += new_msg
            size -= len(new_msg)
        return msg
    
    def __repr__(self) -> str:
        return f'{self.host}:{self.port}'