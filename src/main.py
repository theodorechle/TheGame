import os, sys

gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')
sys.path.append(gui_path)

import pygame
pygame.init()

WIDTH = 1500
HEIGHT = 980
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

from player import Player
from map_generation import MapGenerator
from chunk_manager import Chunk
from save_manager import SaveManager
from entity import Entity
from blocks_menus.block_menu import BlockMenu
from gui.ui_manager import UIManager
from typing import Any
from module_infos import SRC_PATH

from time import monotonic
import menus
import blocks
import random
import items

class Game:
    def __init__(self, window: pygame.Surface) -> None:
        self.FPS: int = 20
        self.WIDTH: int = 1500
        self.HEIGHT: int = 980
        self.window: pygame.Surface = window
        self.last_time_in_menu: float = 0
        self.time_before_menu: float = 0.3
        self.keyboard_keys: dict[str, int] = {
            "mv_left": pygame.K_q, #moves
            "mv_right": pygame.K_d,
            "mv_up": pygame.K_z,
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
            "interact": pygame.K_e,
        }
        self.mouse_buttons: dict[str, int] = {
            "place_block": pygame.BUTTON_LEFT,
            "remove_block": pygame.BUTTON_RIGHT
        }
        self.pressed_keys: dict[str, bool] = {}
        for key in self.keyboard_keys.keys():
            self.pressed_keys[key] = False
        for key in self.mouse_buttons.keys():
            self.pressed_keys[key] = False
        self.run()

    def game_loop(self, map_generator: MapGenerator, save_manager: SaveManager, player: Player) -> int:
        # reload theme on each game
        self._ui_manager.update_theme(os.path.join(SRC_PATH, 'resources', 'gui_themes', 'inventory.json'))
        exit_code = menus.EXIT
        clock = pygame.time.Clock()
        pygame.key.set_repeat(100, 100)
        last_time_toggled_menu = 0
        min_time_before_toggling_menu = 0.5
        loop = True
        need_update: bool = True
        entities: list[Entity] = []
        for i in range(10):
            entities.append(Entity('stone', i, Chunk.HEIGHT, 0, 0, False, self._ui_manager, 1, 1, map_generator, save_manager, 'persos', True))
        blocks_to_update: list[tuple[int, int, blocks.Block]] = []
        blocks_data: dict[tuple[int, int], dict[str, Any]] = {}
        menu_opened: BlockMenu|type[BlockMenu]|None = None
        block_interacting: tuple[int, int]|None = None
        while loop:
            time_last_update: float = clock.get_rawtime()
            if need_update:
                if menu_opened is None:
                    for entity in entities:
                        for block in blocks_to_update:
                            entity.chunk_manager.replace_block(*block)
                    blocks_to_update.clear()
                    self._ui_manager.get_window().fill("#000000")
                    player.chunk_manager.display_chunks(player.x, player.y)
                    player.display()
                    for entity in entities:
                        entity.display(rel_x=player.x, rel_y=player.y)
                    player.display_hud()
                    self._ui_manager.display(False)
                else:
                    menu_opened.display()
                pygame.display.update()
                need_update = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    exit_code = menus.EXIT
                    break
                if menu_opened is not None:
                    if 'interact' in self.keyboard_keys:
                        exit_key = self.keyboard_keys['interact']
                    else:
                        exit_key = self.mouse_buttons['interact']
                    if menu_opened.process_event(event, exit_key):
                        self.pressed_keys['interact'] = True
                    continue
                self._ui_manager.process_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.last_time_in_menu < monotonic() - self.time_before_menu:
                            player.place_back_dragged_item()
                            exit_code = menus.EscapeMenu(self.window).run()
                            self.last_time_in_menu = monotonic()
                            need_update = True
                            if exit_code == menus.EXIT or exit_code == menus.TO_MAIN_MENU:
                                loop = False
                                break
                            elif exit_code == menus.BACK:
                                need_update = True
                                break
                            elif exit_code == menus.SETTINGS:
                                menu = menus.SettingsMenu(self.window, player.chunk_manager.nb_chunks_by_side, blocks.Block.BLOCK_SIZE)
                                menu.run()
                                self.last_time_in_menu = monotonic()
                                player.chunk_manager.change_nb_chunks(menu.slider_nb_chunks.get_value())
                                blocks.Block.BLOCK_SIZE = menu.slider_zoom.get_value()
                                for block in blocks.BLOCKS_DICT:
                                    block.scale_image()
                                player.scale_image()
                                for entity in entities:
                                    entity.scale_image()
                                need_update = True
                                break
                        
                    for key, value in self.keyboard_keys.items():
                        if event.key == value:
                            self.pressed_keys[key] = True
                            break
                elif event.type == pygame.KEYUP:
                    for key, value in self.keyboard_keys.items():
                        if event.key == value:
                            self.pressed_keys[key] = False
                            break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for key, value in self.mouse_buttons.items():
                        if event.button == value:
                            self.pressed_keys[key] = True
                            break
                elif event.type == pygame.MOUSEBUTTONUP:
                    for key, value in self.mouse_buttons.items():
                        if event.button == value:
                            self.pressed_keys[key] = False
                            break

            if self.pressed_keys['mv_left']:
                player.speed_x = -1
            if self.pressed_keys['mv_right']:
                player.speed_x = 1
            if self.pressed_keys['mv_up']:
                player.speed_y = 1
            if self.pressed_keys['open_inv']:
                need_update = player.main_inventory.toggle_inventory()
            for i in range(10):
                if self.pressed_keys[f'inv_{i}']:
                    player.hot_bar_inventory.set_selected_cell(i, 0)
                    need_update = True

            if self.pressed_keys['place_block']:
                updates = player.place_block(pygame.mouse.get_pos())
                if updates is not None:
                    need_update = True
                    if 'changed_block' in updates:
                        blocks_to_update.append(updates['changed_block'])
            if self.pressed_keys['remove_block']:
                updates = player.remove_block(pygame.mouse.get_pos())
                if updates is not None:
                    need_update = True
                    if 'changed_block' in updates:
                        blocks_to_update.append(updates['changed_block'])
            if self.pressed_keys['interact']:
                if last_time_toggled_menu + min_time_before_toggling_menu < monotonic():
                    if menu_opened is not None:
                        if block_interacting in blocks_data and not blocks_data[block_interacting]:
                            blocks_data.pop(block_interacting)
                        block_interacting = None
                        menu_opened = None
                        need_update = True
                        last_time_toggled_menu = monotonic()
                        for key in self.pressed_keys.keys():
                            self.pressed_keys[key] = False
                        pygame.event.clear()
                    else:
                        menu_opened, block_interacting = player.interact_with_block(pygame.mouse.get_pos())
                        if menu_opened is not None:
                            need_update = True
                            block_data = blocks_data.get(block_interacting, None)
                            if block_data is None:
                                block_data = {}
                            menu_opened = menu_opened(block_data, player.hot_bar_inventory, self.window)
                            last_time_toggled_menu = monotonic()
                            for key in self.pressed_keys.keys():
                                self.pressed_keys[key] = False
                            pygame.event.clear()
            
            need_update = player.update(time_last_update) or need_update
            for entity in entities:
                entity.speed_x += random.randint(-1, 1)
                need_update = entity.update(time_last_update) or need_update
            if menu_opened is not None:
                need_update = menu_opened.update() or need_update
            else:
                need_update = self._ui_manager.update() or need_update
            clock.tick(self.FPS)
        player.save()
        save_manager.save_players([player])
        save_manager.save_generation_infos(map_generator.get_infos_to_save())
        return exit_code

    def run(self) -> None:
        self._ui_manager = UIManager(self.window)
        while True:
            save_name = ''
            main_menu = menus.MainMenu(self.window)
            exit_code = main_menu.run()
            if exit_code == menus.EXIT:
                break
            elif exit_code == menus.CREATE_GAME:
                create_world_menu = menus.CreateWorldMenu(self.window)
                exit_code = create_world_menu.run()
                if exit_code == menus.EXIT:
                    break
                save_name = create_world_menu.world_name_text_box.get_text().rstrip()
                seed = create_world_menu.seed_text_box.get_text()
                if not seed:
                    seed = None
                map_generator = MapGenerator(seed)
                save_manager = SaveManager(save_name)
                map_generator.create_seeds()
                player = Player('base_character', 0, Chunk.HEIGHT, 0, 0, False, self._ui_manager, map_generator, save_manager)
                player.hot_bar_inventory.add_element(items.WORKBENCH, 5)
                player.hot_bar_inventory.add_element(items.FURNACE, 5)
            elif exit_code == menus.LOAD_SAVE:
                load_save_menu = menus.LoadSaveMenu(self.window)
                exit_code = load_save_menu.run()
                if exit_code == menus.EXIT:
                    break
                elif exit_code == menus.BACK:
                    continue
                save_manager = SaveManager(load_save_menu.saves_list.child_selected.get_text())
                generation_infos = save_manager.load_generation_infos()
                map_generator = MapGenerator()
                map_generator.set_infos(generation_infos)
                players_dict = save_manager.load_players()
                players = []
                for player, values in players_dict.items():
                    players.append(Player(
                        player,
                        values['x'],
                        values['y'],
                        values['speed_x'],
                        values['speed_y'],
                        values['direction'],
                        self._ui_manager,
                        map_generator,
                        save_manager,
                        values['main_inventory'],
                        values['hot_bar_inventory']
                        )
                    )
                player = players[0]
            if exit_code == menus.START_GAME:
                exit_code = self.game_loop(map_generator, save_manager, player)
                if exit_code == menus.EXIT:
                    break
                elif exit_code == menus.TO_MAIN_MENU:
                    pass
        pygame.quit()

hud_size = 1 # percentage

game = Game(window)
