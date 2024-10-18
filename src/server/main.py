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
In server sent messages, data is optionnal
"""
from multiprocessing import Queue

import json
import struct
import os
import asyncio
from typing import Any
from module_infos import SAVES_PATH
from game import Game
from logs import write_log
import traceback
from save_manager import SaveManager

class Server:
    WRONG_REQUEST = 0
    VALID_REQUEST = 1
    def __init__(self, host: str, port: int) -> None:
        self.running = True
        self.host = host
        self.port = port
        # address, sockets
        self.clients: dict[tuple[str, int], tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
        # game, players addresses
        self.games: dict[Game, list[tuple[str, int]]] = {}
        # actions queue
        self.games_queues: dict[Game, Queue] = {}
        # player address, (player name, game)
        self.players: dict[tuple[str, int], tuple[str, Game]] = {}
        self.players_names: dict[str, tuple[str, int]] = {}
        self.updates_queue = Queue()
    
    async def run(self) -> None:
        write_log(f"launched server on {self.host}:{self.port}")
        self.server = await asyncio.start_server(self.handle_client_request, self.host, self.port)
        async with self.server:
            await asyncio.gather(
                self.process_updates(),
                self.server.serve_forever(),
            )
            
    def close(self) -> None:
        self.server.close()

    async def send_json(self, writer: asyncio.StreamWriter, request: dict) -> None:
        json_request = json.dumps(request)
        write_log(f"Sending {request}")
        bytes_request = json_request.encode()
        message = struct.pack('>I', len(bytes_request)) + bytes_request
        writer.write(message)
        await writer.drain()

    async def send_invalid_request(self, writer: asyncio.StreamWriter) -> None:
        await self.send_json(writer, {
            'status': self.WRONG_REQUEST
        })

    async def send_data(self, writer: asyncio.StreamWriter, data: dict[Any, Any], status: int=VALID_REQUEST) -> None:
        message = {
            'status': status,
            'data': data
        }
        await self.send_json(writer, message)

    async def receive_msg(self, reader: asyncio.StreamReader) -> dict:
        raw_msglen = await self.recvall(reader, 4)
        if not raw_msglen: return {}
        msglen = struct.unpack('>I', raw_msglen)[0]
        message = await self.recvall(reader, msglen)
        if not message: return {}
        return json.loads(message)
    
    async def recvall(self, reader: asyncio.StreamReader, size: int) -> bytes:
        msg = b''
        while size:
            new_msg = await reader.readexactly(size)
            if not new_msg:
                return b''
            msg += new_msg
            size -= len(new_msg)
        return msg

    async def handle_client_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        self.clients[addr] = (reader, writer)
        write_log(f"Client with address {addr} connected")
        try:
            while True:
                try:
                    request = await self.receive_msg(reader)
                except asyncio.IncompleteReadError:
                    write_log(f"Client {addr} disconnected")
                    self.clients.pop(addr)
                    break
                write_log(f"Client {addr} sent request {request}")
                if 'method' not in request or not isinstance(request['method'], str):
                    write_log(f"Bad request: missing 'method' in {request}")
                    await self.send_invalid_request(writer)
                    continue
                match request['method'].upper():
                    case 'GET':
                        await self.handle_get(request, writer)
                    case 'DELETE':
                        await self.handle_delete(request, writer)
                    case 'POST':
                        await self.handle_post(request, writer)
                    case value: # treat as an error
                        write_log(f"Bad request: wrong value for 'method': {value}")
                        await self.send_invalid_request(writer)
        except BaseException as e:
            write_log(f'Error handling client {addr}: {repr(e)}', is_err=True)
            write_log(f'Detail: {traceback.format_exc()}', is_err=True)
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except (OSError, ConnectionResetError):
                write_log(f"Couldn't close connection properly for client {addr}", is_err=True)
            finally:
                if addr in self.players:
                    game = self.players[addr][1]
                    game.remove_player(self.players[addr][0])
                    if game.get_nb_players() == 0:
                        game.save()
                        self.games.pop(game)
                        self.games_queues.pop(game)
                    write_log(f"Removed client {addr} from clients' list")
                else:
                    write_log(f"Unknown client disconnected: `{addr}`")

    async def get_data(self, request: dict, writer: asyncio.StreamWriter) -> dict|None:
        if not isinstance(request.get('data', None), dict):
            write_log(f"Bad request: missing 'data' in {request}")
            await self.send_invalid_request(writer)
            return
        data = request['data']
        if 'type' not in data:
            write_log(f"Bad request: missing 'type' in data {data}")
            await self.send_invalid_request(writer)
            return
        return data

    async def get_values(self, data: dict, values: list[Any], writer: asyncio.StreamWriter) -> tuple[bool, list[Any]]:
        result_values: list[Any] = []
        for value in values:
            if value not in data:
                write_log(f"Bad request: missing '{value}' in data {data}")
                await self.send_invalid_request(writer)
                return (False, result_values)
            result_values.append(data[value])
        return (True, result_values)

    async def handle_get(self, request: dict, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        data: dict|None = await self.get_data(request, writer)
        if data is None: return
        match data['type']:
            case 'saves-list':
                await self.send_data(writer, {'saves': os.listdir(SAVES_PATH)})
            case 'create-world':
                await self.create_world(data, writer)
            case 'join-world':
                await self.join_world(data, writer)
            case 'load-world':
                await self.load_world(data, writer)
            case 'chunk':
                success, values = await self.get_values(data, ['id'], writer)
                if not success:
                    write_log(f"Bad request: missing value 'value'")
                    await self.send_invalid_request(writer)
                if addr not in self.players:
                    write_log(f"Client {addr} tried to get chunk {values[0]} while not playing")
                    await self.send_invalid_request(writer)
                player_name, game = self.players[addr]
                chunk = game.chunk_manager.load_chunk(player_name, values[0])
                if chunk is None:
                    await self.send_invalid_request(writer)
                    return
                await self.send_data(writer, {
                        'type': 'chunk',
                        'chunk': chunk.get_infos_dict()
                })
            case 'game-infos':
                await self.send_data(writer, {
                    'type': 'game-infos',
                    'infos': self.players[addr][1].get_infos()
                })
            case values:
                write_log(f"Bad request: wrong value for data type: '{values}'")
                await self.send_invalid_request(writer)

    async def handle_delete(self, request: dict, writer: asyncio.StreamWriter) -> None:
        data: dict|None = await self.get_data(request, writer)
        if data is None: return
        match data['type']:
            case 'save':
                saves_names = request['data'].get('names', None)
                if saves_names is None: return
                for save_name in saves_names:
                    save_path = os.path.join(SAVES_PATH, save_name)
                    if os.path.isdir(save_path):
                        delete_folder(save_path)
            case value:
                write_log(f"Bad request: wrong value for data type: '{value}'")
                await self.send_invalid_request(writer)

    async def handle_post(self, request: dict, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        data: dict|None = await self.get_data(request, writer)
        if data is None: return
        match data['type']:
            case 'update':
                success, values = await self.get_values(data, ['actions'], writer)
                if not success: return
                player_name, game = self.players[addr]
                actions_queue = self.games_queues[game]
                actions_queue.put({'name': player_name, 'actions': values[0], 'additional_data': data.get('additional_data')})
            case 'chunks':
                success, values = await self.get_values(data, ['ids'], writer)
                if not success: return
                player_name, game = self.players[addr]
                game.chunk_manager.save_chunks(player_name, values[0])
            case value:
                write_log(f"Bad request: wrong value for data type: '{value}'")
                await self.send_invalid_request(writer)

    async def process_updates(self) -> None:
        while True:
            player_name, update_dict = await asyncio.get_event_loop().run_in_executor(None, self.updates_queue.get)
            player_addr: tuple[str, int]|None = self.players_names.get(player_name, None)
            if player_addr is None or player_addr not in self.clients: continue
            update_dict['type'] = 'player-update'
            await self.send_json(self.clients[player_addr][1], {
                'status': self.VALID_REQUEST,
                'data': update_dict
            })
            # TODO: remove player from game

    async def create_world(self, data: dict, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        success, values = await self.get_values(data, ['seed', 'save', 'player-name'], writer)
        if not success:
            write_log(f"Client {addr} tried to create game but send partial data: '{data}'")
            await self.send_invalid_request(writer)
            return
        if addr in self.players:
            write_log(f"Client {addr} tried to create game but was already playing: '{data}'")
            await self.send_invalid_request(writer)
            return
        seed, save, player_name = values
        if SaveManager.save_already_exists(save):
            await self.send_invalid_request(writer)
            return
        
        actions_queue = Queue()
        game = Game(seed, save, actions_queue, self.updates_queue)
        asyncio.create_task(game.run())
        game.create_player(player_name, data.get('player-images-name', ''))
        self.games[game] = [addr]
        self.games_queues[game] = actions_queue
        self.players[addr] = (player_name, game)
        self.players_names[player_name] = addr
        await self.send_json(writer, {'status': self.VALID_REQUEST})

    async def join_world(self, data: dict, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        if addr in self.players:
            write_log(f"Client {addr} tried to join game but was already playing: '{data}'")
            await self.send_invalid_request(writer)
            return
        success, values = await self.get_values(data, ['game', 'player-name'], writer)
        if not success:
            write_log(f"Client {addr} tried to join game but send partial data: '{data}'")
            await self.send_invalid_request(writer)
            return
        searched_game_name, player_name = values
        for game in self.games.keys():
            if game.get_name() == searched_game_name:
                game.create_player(player_name, data.get('player-images-name', ''))
                self.players[addr] = (player_name, game)
                self.players_names[player_name] = addr
                await self.send_json(writer, {'status': self.VALID_REQUEST})
                return
        await self.send_invalid_request(writer)
    
    async def load_world(self, data: dict, writer: asyncio.StreamWriter) -> None:
        addr = writer.get_extra_info('peername')
        if addr in self.players:
            write_log(f"Client {addr} tried to load game but was already playing: '{data}'")
            await self.send_invalid_request(writer)
            return
        success, values = await self.get_values(data, ['save', 'player-name'], writer)
        if not success:
            write_log(f"Client {addr} tried to join game but send partial data: '{data}'")
            await self.send_invalid_request(writer)
            return
        save_name, player_name = values
        if not SaveManager.save_already_exists(save_name):
            self.send_invalid_request()
            return
        
        actions_queue = Queue()
        game = Game(None, save_name, actions_queue, self.updates_queue)
        asyncio.create_task(game.run())
        game.create_player(player_name, data.get('player-images-name', ''))
        self.games[game] = [addr]
        self.games_queues[game] = actions_queue
        self.players[addr] = (player_name, game)
        self.players_names[player_name] = addr
        await self.send_json(writer, {'status': self.VALID_REQUEST})


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
    write_log(f'Detail: {traceback.format_exc()}', is_err=True)
