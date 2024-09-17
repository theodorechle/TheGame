import sys
from module_infos import GUI_PATH, RESOURCES_PATH
sys.path.append(GUI_PATH)

import os
from time import monotonic

import menus
import pygame
pygame.init()
WIDTH = 1500
HEIGHT = 980
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

from server_connection import ServerConnection
from gui.ui_manager import UIManager
from gui import elements
from player import Player
from entity import DrawableEntity
import blocks
from typing import Any
import asyncio
from map_chunk import Chunk

class Client:
    PORT = 12345
    def __init__(self, window) -> None:
        self.exit = False
        self.server = ServerConnection('127.0.0.1', self.PORT)
        self.MAX_FPS = 20

        self.player_name = 'base_character'
        self.player_images_name = 'base_character'
        self.player = None
        self.others_players: dict[str, DrawableEntity] = {}

        self.last_time_in_menu: float = 0
        self.min_time_before_toggling_menu: float = 0.3

        # UI
        self.window = window
        self._ui_manager = UIManager(self.window)
        self._ui_manager.update_theme(os.path.join(RESOURCES_PATH, 'gui_themes', 'player_name.json'))

        # keys
        self.server_actions_keyboard_keys: dict[str, int] = {
            "mv_left": pygame.K_q, # moves
            "mv_right": pygame.K_d,
            "mv_up": pygame.K_z
        }

        self.client_actions_keyboard_keys: dict[str, int] = {
            "inv_0": pygame.K_1, # inventory
            "inv_1": pygame.K_2,
            "inv_2": pygame.K_3,
            "inv_3": pygame.K_4,
            "inv_4": pygame.K_5,
            "inv_5": pygame.K_6,
            "inv_6": pygame.K_7,
            "inv_7": pygame.K_8,
            "inv_8": pygame.K_9,
            "inv_9": pygame.K_0,
            "open_inv": pygame.K_i,
            "interact": pygame.K_e
        }
        self.mouse_buttons: dict[str, int] = {
            "place_block": pygame.BUTTON_LEFT,
            "remove_block": pygame.BUTTON_RIGHT
        }
        self.server_actions_pressed_keys: dict[str, bool] = {}
        for key in self.server_actions_keyboard_keys.keys():
            self.server_actions_pressed_keys[key] = False
        self.client_actions_pressed_keys: dict[str, bool] = {}
        for key in self.server_actions_keyboard_keys.keys():
            self.client_actions_pressed_keys[key] = False
        for key in self.mouse_buttons.keys():
            self.server_actions_pressed_keys[key] = False
    
    async def start(self) -> None:
        await self.server.start()

    async def run_menus(self) -> bool:
        """
        Returns True if a game is started else False
        """
        while True:
            main_menu = menus.MainMenu(self.window, self.server)
            exit_code = main_menu.run()
            if exit_code == menus.EXIT:
                self.exit = True
                break
            player_name = main_menu.player_name_input.get_text()
            if not player_name: continue
            self.player_name = player_name
            if exit_code == menus.CREATE_WORLD:
                create_world_menu = menus.CreateWorldMenu(self.window, self.server)
                exit_code = create_world_menu.run()
                if exit_code == menus.BACK: continue
                save_name = create_world_menu.world_name_text_box.get_text().strip()
                seed = create_world_menu.seed_text_box.get_text()
                if not seed:
                    seed = None
                await self.server.send_json({
                    'method': 'GET',
                    'data': {
                        'type': 'create-world',
                        'seed': seed,
                        'save': save_name,
                        'player-name': self.player_name,
                        'player-images-name': self.player_images_name
                    }
                })
                response = await self.server.receive_msg()
                if response['status'] == ServerConnection.WRONG_REQUEST: continue
                return True
            if exit_code == menus.JOIN_WORLD:
                join_world_menu = menus.JoinWorldMenu(self.window, self.server)
                exit_code = join_world_menu.run()
                if exit_code == menus.BACK: continue
                host_address = join_world_menu.host_address_text_box.get_text().strip()
                game_name = join_world_menu.world_name_text_box.get_text().strip()
                self.server.stop()
                self.server = ServerConnection(host_address, self.PORT)
                try:
                    await self.server.start()
                except ConnectionError:
                    continue
                await self.server.send_json({
                    'method': 'GET',
                    'data': {
                        'type': 'join',
                        'game': game_name,
                        'player-name': self.player_name,
                        'player-images-name': self.player_images_name
                    }
                })
                response = await self.server.receive_msg()
                if response['status'] == ServerConnection.WRONG_REQUEST: continue
                return True
            if exit_code == menus.LOAD_SAVE:
                exit_code = menus.LoadSaveMenu(self.window, self.server).run()
                if exit_code == menus.BACK: continue
        return False

    def stop_client(self, _: elements.TextButton) -> None:
        self.exit = True

    async def run(self) -> None:
        self.player = Player(self.player_name, 0, Chunk.HEIGHT, 0, 0, False, self._ui_manager, self.server, images_name=self.player_images_name)
        await self.player.initialize_chunks()
        tasks = [asyncio.create_task(self.loop()), asyncio.create_task(self.process_socket_messages())]
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for p in pending:
            p.cancel()

    async def loop(self) -> None:
        clock = pygame.time.Clock()
        while not self.exit:
            if await self.update():
                self.server.stop()
                break # exit
            self.display()
            clock.tick(self.MAX_FPS)
            await asyncio.sleep(0.2)

    async def update(self) -> bool:
        for event in pygame.event.get():
            self._ui_manager.process_event(event)
            if event.type == pygame.QUIT:
                self.exit = True
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.last_time_in_menu < monotonic() - self.min_time_before_toggling_menu:
                        self.player.place_back_dragged_item()
                        exit_code = menus.EscapeMenu(self.window, self.server).run()
                        self.last_time_in_menu = monotonic()
                        if exit_code == menus.EXIT or exit_code == menus.TO_MAIN_MENU:
                            return True
                        elif exit_code == menus.BACK:
                            break
                        elif exit_code == menus.SETTINGS:
                            menu = menus.SettingsMenu(self.window, self.player.chunk_manager.nb_chunks_by_side, blocks.Block.BLOCK_SIZE)
                            menu.run()
                            self.last_time_in_menu = monotonic()
                            self.player.chunk_manager.change_nb_chunks(menu.slider_nb_chunks.get_value())
                            blocks.Block.BLOCK_SIZE = menu.slider_zoom.get_value()
                            for block in blocks.BLOCKS_DICT:
                                block.scale_image()
                            self.player.scale_image()
                            for player in self.others_players.values():
                                player.scale_image()
                            break
                    
                for key, value in self.server_actions_keyboard_keys.items():
                    if event.key == value:
                        self.server_actions_pressed_keys[key] = True
                        break
                for key, value in self.client_actions_pressed_keys.items():
                    if event.key == value:
                        self.client_actions_pressed_keys[key] = True
                        break
            elif event.type == pygame.KEYUP:
                for key, value in self.server_actions_keyboard_keys.items():
                    if event.key == value:
                        self.server_actions_pressed_keys[key] = False
                        break
                for key, value in self.client_actions_pressed_keys.items():
                    if event.key == value:
                        self.client_actions_pressed_keys[key] = False
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for key, value in self.mouse_buttons.items():
                    if event.button == value:
                        self.server_actions_pressed_keys[key] = True
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                for key, value in self.mouse_buttons.items():
                    if event.button == value:
                        self.server_actions_pressed_keys[key] = False
                        break
    
        self._ui_manager.update()
        actions: list[str] = [action for action, is_done in self.server_actions_pressed_keys.items() if is_done]
        if actions:
            await self.server.send_json({
                'method': 'POST',
                'data': {
                    'type': 'update',
                    'actions': actions
                }
            })
        return False

    async def process_socket_messages(self) -> None:
        while not self.exit:
            message_dict = await self.server.receive_msg()
            if not message_dict: return
            if 'data' not in message_dict:
                continue
            data = message_dict['data']
            if 'type' not in data: continue
            match data['type']:
                case 'player-update':
                    await self.update_player(data)
                case 'chunk':
                    self.player.chunk_manager.set_chunk(message_dict)
    
    async def update_player(self, data: dict[str, Any]) -> None:
        if 'players' not in data: return
        for player_name, player_data in data['players'].items():
            if player_name == self.player_name:
                await self.player.update(player_data)
            else:
                if player_name not in self.others_players:
                    self.others_players[player_name] = DrawableEntity(player_name, 0, 0, 0, 0, False, 1, 2, self._ui_manager, 'persos', True, images_name=player_data.get('images-name', ''), display_name=True)
                self.others_players[player_name].update(player_data)
        self.display()

    def display(self) -> None:
        self.player.display()
        for player in self.others_players.values():
            player.display(self.player.x, self.player.y)
        self.player.display_hud()
        self._ui_manager.display()
        pygame.display.update()

async def start() -> None:
    client = Client(window)
    try:
        await client.start()
    except ConnectionError:
        print("Can't connect to local server")
        return
    do_run_main: bool = await client.run_menus()
    if do_run_main:
        await client.run()

asyncio.run(start())