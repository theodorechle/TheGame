import sys
from module_infos import GUI_PATH
sys.path.append(GUI_PATH)
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
import blocks
from typing import Any
import asyncio
from map_chunk import Chunk

class Client:
    def __init__(self, window) -> None:
        self.exit = False
        self.server = ServerConnection('127.0.0.1', 12345)
        self.MAX_FPS = 20

        self.player_name = 'base_character'
        self.player = None

        self.last_time_in_menu: float = 0
        self.min_time_before_toggling_menu: float = 0.3

        # UI
        self.window = window
        self._ui_manager = UIManager(self.window)

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
        await self.server.connect_to_server()

    async def run_menus(self) -> bool:
        """
        Returns True if a game is started else False
        """
        while True:
            exit_code = menus.MainMenu(self.window, self.server).run()
            if exit_code == menus.EXIT:
                self.exit = True
                break
            elif exit_code == menus.CREATE_GAME:
                create_world_menu = menus.CreateWorldMenu(self.window, self.server)
                exit_code = create_world_menu.run()
                if exit_code == menus.BACK:
                    continue
                save_name = create_world_menu.world_name_text_box.get_text().rstrip()
                seed = create_world_menu.seed_text_box.get_text()
                if not seed:
                    seed = None
                await self.server.send_json({
                    'method': 'GET',
                    'data': {
                        'type': 'create-world',
                        'seed': seed,
                        'save': save_name,
                        'player-name': self.player_name
                    }
                })
                response = await self.server.receive_msg()
                if response['status'] == ServerConnection.WRONG_REQUEST:
                    continue
                return True
            elif exit_code == menus.LOAD_SAVE:
                exit_code = menus.LoadSaveMenu(self.window, self.server).run()
                if exit_code == menus.BACK:
                    continue
        return False

    def stop_client(self, _: elements.TextButton) -> None:
        self.exit = True

    async def run(self) -> None:
        self.player = Player(self.player_name, 0, Chunk.HEIGHT, 0, 0, False, self._ui_manager, self.server)
        await self.player.initialize_chunks()
        await asyncio.gather(self.loop(), self.process_socket_messages())

    async def loop(self) -> None:
        clock = pygame.time.Clock()
        while not self.exit:
            if await self.update():
                break # exit
            self.display()
            clock.tick(self.MAX_FPS)
            await asyncio.sleep(0.2)

    async def update(self) -> bool:
        for event in pygame.event.get():
            self._ui_manager.process_event(event)
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
                            # for entity in entities:
                            #     entity.scale_image()
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
        await self.server.send_json({
            'method': 'POST',
            'data': {
                'type': 'update',
                'actions': [action for action, is_done in self.server_actions_pressed_keys.items() if is_done]
            }
        })
        return False

    async def process_socket_messages(self) -> None:
        while True:
            message_dict = await self.server.receive_msg()
            if not message_dict: return
            if 'data' not in message_dict:
                continue
            data = message_dict['data']
            if data['type'] == 'player-update':
                self.update_player(data)
            elif data['type'] == 'chunk':
                self.player.chunk_manager.set_chunk(message_dict)
        
    
    def update_player(self, data: dict[str, Any]) -> None:
        self.player.x = data['players'][self.player_name]['x']
        self.player.y = data['players'][self.player_name]['y']
        self.display()

    def display(self) -> None:
        self.player.display()
        self.player.display_hud()
        self._ui_manager.display()
        pygame.display.update()

async def start() -> None:
    client = Client(window)
    await client.start()
    do_run_main: bool = await client.run_menus()
    if do_run_main:
        await client.run()

asyncio.run(start())