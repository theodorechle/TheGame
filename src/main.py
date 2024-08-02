import os, sys
gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')
sys.path.append(gui_path)


import pygame
from gui.ui_manager import UIManager
pygame.init()

WIDTH = 1500
HEIGHT = 980
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

from player import Player
from map_generation import MapGenerator
from chunk_manager import Chunk
from save_manager import SaveManager
from entity import Entity

from time import monotonic
import menus
import blocks
import random

class Game:
    def __init__(self, window: pygame.Surface) -> None:
        self.FPS: int = 20
        self.WIDTH: int = 1500
        self.HEIGHT: int = 980
        self.window: pygame.Surface = window
        self.last_time_in_menu: float = 0
        self.time_before_menu: float = 0.3
        self.keys: dict[str, int] = {
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
            "open_inv": pygame.K_i
        }
        self.pressed_keys: dict[str, bool] = {
            "mv_left": False,
            "mv_right": False,
            "mv_up": False,
            "inv_0": False,
            "inv_1": False,
            "inv_2": False,
            "inv_3": False,
            "inv_4": False,
            "inv_5": False,
            "inv_6": False,
            "inv_7": False,
            "inv_8": False,
            "inv_9": False,
            "open_inv": False
        }
        self.run()

    def game_loop(self, map_generator: MapGenerator, save_manager: SaveManager, player: Player) -> int:
        exit_code = menus.EXIT
        clock = pygame.time.Clock()
        pygame.key.set_repeat(100, 100)
        loop = True
        need_update = True
        entities: list[Entity] = []
        for i in range(5):
            entities.append(Entity('base_character', i, Chunk.HEIGHT, 0, 0, False, self.window, 1, 2, map_generator, save_manager, 'persos', True))
        blocks_to_update: list[tuple[int, int, blocks.Block]] = []
        while loop:
            time_last_update: float = clock.get_rawtime()
            if need_update:
                for entity in entities:
                    for block in blocks_to_update:
                        entity.chunk_manager.replace_block(*block)
                blocks_to_update.clear()
                self.window.fill("#000000", pygame.Rect(0, 0, self.WIDTH, self.HEIGHT))
                player.chunk_manager.display_chunks(player.x, player.y)
                player.display()
                for entity in entities:
                    entity.display(rel_x=player.x, rel_y=player.y)
                player.display_hud()
                pygame.display.update()
                need_update = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    exit_code = menus.EXIT
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.last_time_in_menu > monotonic() - self.time_before_menu: continue
                        player.inventory.place_back_clicked_item()
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
                    if event.key == self.keys['mv_left']:
                        self.pressed_keys['mv_left'] = True
                    elif event.key == self.keys['mv_right']:
                        self.pressed_keys['mv_right'] = True
                    elif event.key == self.keys['mv_up']:
                        self.pressed_keys['mv_up'] = True
                    elif event.key == self.keys['open_inv']:
                        self.pressed_keys['open_inv'] = True
                    else:
                        for i in range(10):
                            if event.key == self.keys[f'inv_{i}']:
                                self.pressed_keys[f'inv_{i}'] = True
                elif event.type == pygame.KEYUP:
                    if event.key == self.keys['mv_left']:
                        self.pressed_keys['mv_left'] = False
                    elif event.key == self.keys['mv_right']:
                        self.pressed_keys['mv_right'] = False
                    elif event.key == self.keys['mv_up']:
                        self.pressed_keys['mv_up'] = False
                    else:
                        for i in range(10):
                            if event.key == self.keys[f'inv_{i}']:
                                self.pressed_keys[f'inv_{i}'] = False


            if self.pressed_keys['mv_left']:
                player.speed_x = -1
            if self.pressed_keys['mv_right']:
                player.speed_x = 1
            if self.pressed_keys['mv_up']:
                player.speed_y = 1
            if self.pressed_keys['open_inv']:
                need_update = player.inventory.toggle_inventory()
                self.pressed_keys['open_inv'] = False
            for i in range(10):
                if self.pressed_keys[f'inv_{i}']:
                    player.inventory.selected = i
                    need_update = True

            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                updates = player.place_block(pygame.mouse.get_pos())
                if updates is not None:
                    need_update = True
                    if 'changed_block' in updates:
                        blocks_to_update.append(updates['changed_block'])
            if pressed_mouse_buttons[2]:
                updates = player.remove_block(pygame.mouse.get_pos())
                if updates is not None:
                    need_update = True
                    if 'changed_block' in updates:
                        blocks_to_update.append(updates['changed_block'])

            need_update = player.update(time_last_update) or need_update
            for entity in entities:
                entity.speed_x += random.randint(-1, 1)
                need_update = entity.update(time_last_update) or need_update
            clock.tick(self.FPS)
        player.save()
        save_manager.save_players([player])
        save_manager.save_generation_infos(map_generator.get_infos_to_save())
        return exit_code

    def run(self) -> None:
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
                player = Player('base_character', 0, Chunk.HEIGHT, 0, 0, False, self.window, map_generator, save_manager)
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
                        self.window,
                        map_generator,
                        save_manager,
                        values['inventory']
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
