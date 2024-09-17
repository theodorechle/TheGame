import subprocess
import asyncio
import struct
import json
import sys
import os
from module_infos import SERVER_PATH

class ServerConnection:
    VALID_REQUEST = 1
    WRONG_REQUEST = 0
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        # self.server_process = subprocess.Popen(
        #     [sys.executable, os.path.join(SERVER_PATH, 'main.py')],
        #     stdout=sys.stdout,
        #     stderr=sys.stderr,
        #     start_new_session=True)

    def stop(self) -> None:
        self.writer.close()
        # self.server_process.kill()

    async def start(self) -> None:
        try:
            self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), timeout=1)
        except asyncio.TimeoutError:
            raise ConnectionError
        if self.reader is None or self.writer is None:
            raise ConnectionError

    async def send_json(self, request: dict) -> None:
        request = json.dumps(request).encode()
        message = struct.pack('>I', len(request)) + request
        self.writer.write(message)
        await self.writer.drain()
    
    async def receive_msg(self, ) -> dict:
        raw_msglen = await self.recvall(4)
        if not raw_msglen:
            return {}
        msglen = struct.unpack('>I', raw_msglen)[0]
        message = await self.recvall(msglen)
        if not message:
            return {}
        return json.loads(message)    
    
    async def recvall(self, size: int) -> bytes:
        msg = b''
        while size:
            new_msg = await self.reader.readexactly(size)
            if not new_msg:
                return b''
            msg += new_msg
            size -= len(new_msg)
        return msg