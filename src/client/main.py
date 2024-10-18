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
pygame.display.set_caption("The game")

from server_connection import ServerConnection
from gui.ui_manager import UIManager
from gui import elements
from entities.player import Player
from entities.entity import DrawableEntity
import blocks
from typing import Any
import asyncio
from map_chunk import Chunk
import traceback
from logs import write_log

import random

class Client:
    PORT = 12345
    def __init__(self, window: pygame.Surface) -> None:
        self.exit_game = False
        self.exit_program = False
        self.server = ServerConnection('127.0.0.1', self.PORT)
        self.MAX_FPS = 20

        self.player_name = ''
        self.player_images_name = 'base_character'
        self.player = None
        self.others_players: dict[str, DrawableEntity] = {}

        self.last_time_in_menu: float = 0
        self.min_time_before_toggling_menu: float = 0.3

        # UI
        self.window = window
        self._ui_manager = UIManager(self.window)
        self._ui_manager.update_theme(os.path.join(RESOURCES_PATH, 'gui_themes', 'player_name.json'))
        self.need_redraw = False

        # keys
        self.server_actions_keyboard_keys: dict[str, int] = {
            "mv_left": pygame.K_q, # moves
            "mv_right": pygame.K_d,
            "mv_up": pygame.K_z,
            "interact": pygame.K_e
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
        }
        self.server_actions_mouse_buttons: dict[str, int] = {
            "place_block": pygame.BUTTON_LEFT,
            "remove_block": pygame.BUTTON_RIGHT
        }
        self.server_actions_pressed_keys: dict[str, bool] = {key: False for key in self.server_actions_keyboard_keys.keys()}
        self.client_actions_pressed_keys: dict[str, bool] = {key: False for key in self.client_actions_keyboard_keys.keys()}
        self.server_actions_pressed_mouse_keys: dict[str, bool] = {key: False for key in self.server_actions_mouse_buttons.keys()}
    
    async def start(self) -> None:
        self.server.launch_local_server()
        await self.server.start()

    async def stop(self) -> None:
        await self.server.stop()
        self.server.stop_local_server()

    async def run_menus(self) -> bool:
        """
        Returns True if a game is started else False
        """
        while True:
            main_menu = menus.MainMenu(self.window, self.server)
            main_menu.player_name_input.process_event(pygame.event.Event(pygame.TEXTINPUT, {'text': self.player_name}))
            exit_code = main_menu.run()
            if exit_code == menus.EXIT:
                self.exit_program = True
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
                write_log(f"Creating world {save_name} with seed {seed}")
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
                if response['status'] == ServerConnection.WRONG_REQUEST:
                    write_log(f"Server failed to create the world {save_name}")
                    continue
                write_log("World created")
                return True
            elif exit_code == menus.JOIN_WORLD:
                join_world_menu = menus.JoinWorldMenu(self.window, self.server)
                exit_code = join_world_menu.run()
                if exit_code == menus.BACK: continue
                host_address = join_world_menu.host_address_text_box.get_text().strip()
                game_name = join_world_menu.world_name_text_box.get_text().strip()
                new_server = ServerConnection(host_address, self.PORT)
                try:
                    await new_server.start()
                except ConnectionError:
                    continue
                write_log(f"Joining world {game_name} at {host_address}:{self.PORT}")
                await new_server.send_json({
                    'method': 'GET',
                    'data': {
                        'type': 'join-world',
                        'game': game_name,
                        'player-name': self.player_name,
                        'player-images-name': self.player_images_name
                    }
                })
                response = await new_server.receive_msg()
                if response['status'] == ServerConnection.WRONG_REQUEST:
                    write_log(f"Failed to join world {game_name}")
                    continue
                await self.server.stop()
                self.server = new_server
                write_log("World joined")
                return True
            elif exit_code == menus.LOAD_SAVE:
                menu = menus.LoadSaveMenu(self.window, self.server)
                await menu.add_saves()
                exit_code = menu.run()

                await self.server.send_json({
                    'method': 'DELETE',
                    'data': {
                        'type': 'save',
                        'names': menu.saves_to_delete
                    }
                })
                
                if exit_code == menus.BACK: continue
                elif exit_code == menus.START_GAME:
                    save_name = menu.saves_list.child_selected.get_text()
                    await self.server.send_json({
                        'method': 'GET',
                        'data': {
                            'type': 'load-world',
                            'save': save_name,
                            'player-name': self.player_name,
                            'player-images-name': self.player_images_name
                        }
                    })
                    response = await self.server.receive_msg()
                    if response['status'] == ServerConnection.WRONG_REQUEST:
                        write_log(f"Server failed to load the world {save_name}")
                        continue
                    write_log("World loaded")
                    return True
        return False

    def stop_client(self, _: elements.TextButton) -> None:
        self.exit_game = True
        
    async def run_escape_menu(self) -> bool:
        """
        Return True if need to escape the update function to directly go to the loop function
        """
        self.need_redraw = self.need_redraw or self._ui_manager.update()
        self.need_redraw = True                          
        self.player.place_back_dragged_item()
        escape_menu = menus.EscapeMenu(self.window, self.server)
        while True:
            exit_code = escape_menu.run()
            self.last_time_in_menu = monotonic()
            if exit_code == menus.EXIT:
                self.exit_program = True
                return True
            elif exit_code == menus.TO_MAIN_MENU:
                self.exit_game = True
                return True
            elif exit_code == menus.BACK:
                return True
            elif exit_code == menus.SETTINGS:
                settings_menu = menus.SettingsMenu(self.window, self.server, self.player.chunk_manager.nb_chunks_by_side, blocks.block_size)
                exit_code = settings_menu.run()
                self.last_time_in_menu = monotonic()
                await self.player.chunk_manager.change_nb_chunks(settings_menu.slider_nb_chunks.get_value())
                new_block_size = settings_menu.slider_zoom.get_value()
                if new_block_size != blocks.block_size:
                    blocks.block_size = new_block_size
                    for block in blocks.BLOCKS_DICT:
                        block.load_image()
                    self.player.load_image()
                    for player in self.others_players.values():
                        player.load_image()
                    self.player.chunk_manager.scale_chunk_surfaces()
                if exit_code == menus.BACK:
                    return True
                elif exit_code != menus.TO_MAIN_MENU:
                    break
                escape_menu.reset()
        return False

    def process_event(self, events_dict: dict[str, Any], actions_dict: dict[str, bool], tested_event: Any, value_to_assign: bool) -> bool:
        for key, event in events_dict.items():
            if event == tested_event:
                actions_dict[key] = value_to_assign
                return True
        return False

    async def process_events(self) -> bool:
        """
        Return True if need to escape the update function to directly go to the loop function
        """
        for event in pygame.event.get():
            self._ui_manager.process_event(event)
            if event.type == pygame.QUIT:
                self.exit_program = True
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.last_time_in_menu < monotonic() - self.min_time_before_toggling_menu:
                        if await self.run_escape_menu(): return True
                if self.process_event(self.server_actions_keyboard_keys, self.server_actions_pressed_keys, event.key, True): continue
                if self.process_event(self.client_actions_keyboard_keys, self.client_actions_pressed_keys, event.key, True): continue
            elif event.type == pygame.KEYUP:
                if self.process_event(self.server_actions_keyboard_keys, self.server_actions_pressed_keys, event.key, False): continue
                if self.process_event(self.client_actions_keyboard_keys, self.client_actions_pressed_keys, event.key, False): continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.process_event(self.server_actions_mouse_buttons, self.server_actions_pressed_mouse_keys, event.button, True): continue
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.process_event(self.server_actions_mouse_buttons, self.server_actions_pressed_mouse_keys, event.button, False): continue
        return False

    async def run(self) -> bool:
        """
        Returns True if the player wants to exit the program, False if only exiting the actual game
        """
        try:
            self.player = Player(self.player_name, 0, Chunk.HEIGHT, 0, 0, False, self._ui_manager, self.server, images_name=self.player_images_name)
            self._ui_manager.update_theme(os.path.join(RESOURCES_PATH, 'gui_themes', 'inventory.json'))
            await self.player.initialize_chunks()
            tasks = [asyncio.create_task(self.loop()), asyncio.create_task(self.process_socket_messages())]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            write_log(f"Stopped game")
            for p in pending:
                p.cancel()
        except BaseException as e:
            write_log(f'Error in run: {repr(e)}', is_err=True)
            write_log(f'Detail: {traceback.format_exc()}', is_err=True)
        finally:
            try:
                await self.server.stop()
            except (OSError, ConnectionResetError):
                write_log(f"Couldn't close connection with server {self.server}", is_err=True)

    async def loop(self) -> None:
        try:
            while True:
                await self.update()
                if self.exit_game or self.exit_program: return
                if self.need_redraw:
                    self.display()
                    self.need_redraw = False
                await asyncio.sleep(0.05)
        except BaseException as e:
            write_log(f'Error in loop: {repr(e)}', is_err=True)
            write_log(f'Detail: {traceback.format_exc()}', is_err=True)

    async def update(self) -> None:
        if await self.process_events(): return

        # sending random data to the server for DEBUG ONLY

        # for key in self.server_actions_pressed_mouse_keys.keys():
        #     self.server_actions_pressed_mouse_keys[key] = random.randint(0, 1)

        # for key in self.server_actions_pressed_keys.keys():
        #     self.server_actions_pressed_keys[key] = random.randint(0, 1)

        # for key in self.client_actions_pressed_keys.keys():
        #         self.client_actions_pressed_keys[key] = random.randint(0, 1)


        if self.client_actions_pressed_keys['open_inv']:
            self.player.main_inventory.toggle_inventory()
        
        for i in range(10):
            if self.client_actions_pressed_keys[f'inv_{i}']:
                self.player.hot_bar_inventory.set_selected_cell(i, 0)
                self.need_redraw = True
        
        additional_data: dict = {}
        if self.server_actions_pressed_mouse_keys["place_block"]:
            if (block_pos := self.player.place_block(pygame.mouse.get_pos())) is not None:
                additional_data['interacted_block'] = block_pos
                additional_data['selected'] = self.player.hot_bar_inventory.get_selected_index()
        
        if self.server_actions_pressed_mouse_keys["remove_block"]:
            if (block_pos := self.player.remove_block(pygame.mouse.get_pos())) is not None:
                additional_data['interacted_block'] = block_pos

        actions: list[str] = [action for action, is_done in self.server_actions_pressed_keys.items() if is_done]
        actions.extend(action for action, is_done in self.server_actions_pressed_mouse_keys.items() if is_done)
        if actions:
            data = {
                    'type': 'update',
                    'actions': actions
            }
            if additional_data:
                data['additional_data'] = additional_data
            await self.server.send_json({
                'method': 'POST',
                'data': data
            })

    async def process_socket_messages(self) -> None:
        try:
            while not self.exit_game:
                try:
                    message_dict = await self.server.receive_msg()
                except asyncio.IncompleteReadError:
                    write_log("Error while reading input data from server", True)
                    write_log(traceback.format_exc(), True)
                    return
                write_log(f"Server sent message {message_dict}")
                if 'data' not in message_dict:
                    continue
                data = message_dict['data']
                if 'type' not in data: continue
                match data['type']:
                    case 'player-update':
                        await self.update_player(data)
                        self.need_redraw = True
                    case 'chunk':
                        self.player.chunk_manager.set_chunk(message_dict)
                        self.need_redraw = True
                    case 'game-infos':
                        self.player.chunk_manager.create_map_generator(data)
                        self.need_redraw = True
        except BaseException as e:
            write_log(f'Error in process_socket_messages: {repr(e)}', is_err=True)
            write_log(f'Detail: {traceback.format_exc()}', is_err=True)
        
    async def update_player(self, data: dict[str, Any]) -> None:
        if 'players' not in data: return
        for player_name, player_data in data['players'].items():
            if player_name == self.player_name:
                await self.player.update(player_data)
            else:
                if 'removed' in player_data:
                    self.others_players[player_name].delete()
                    self.others_players.pop(player_name, None)
                    continue
                if player_name not in self.others_players:
                    self.others_players[player_name] = DrawableEntity(player_name, 0, 0, 0, 0, False, 1, 2, self._ui_manager, 'persos', True, images_name=player_data.get('images-name', ''), name_displayed=True)
                self.others_players[player_name].update(player_data)
        if 'blocks' not in data: return
        for pos, block in zip(*data['blocks']):
            self.player.chunk_manager.replace_block(*pos, blocks.REVERSED_BLOCKS_DICT[block])

    def display(self) -> None:
        self.window.fill("#000000")
        self.player.display()
        for player in self.others_players.values():
            player.display(self.player.x, self.player.y)
            player.display_name(self.player.x, self.player.y)
        self.player.display_hud()
        self._ui_manager.display(False)
        pygame.display.update()

async def start() -> None:
    client = Client(window)
    try:
        while not client.exit_program:
            client.exit_game = False
            try:
                await client.start()
            except ConnectionError:
                write_log("Can't connect to local server", is_err=True)
                return
            do_run_main: bool = await client.run_menus()
            if do_run_main:
                await client.run()
    except BaseException:
        client.stop()
        raise

try:
    asyncio.run(start())
except BaseException as e:
    write_log(f'Error in process_socket_messages: {repr(e)}', is_err=True)
    write_log(f'Detail: {traceback.format_exc()}', is_err=True)