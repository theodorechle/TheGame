import os, sys
gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')
sys.path.append(gui_path)


import pygame
from gui.ui_manager import UIManager
pygame.init()

WIDTH = 1500
HEIGHT = 980
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
ui_manager = UIManager(window)

from player import Player
from map_generation import MapGenerator
from chunk_manager import Chunk
from save_manager import SaveManager

from time import monotonic

import menus

class Game:
    def __init__(self, window: pygame.Surface, ui_manager: UIManager) -> None:
        self.FPS: int = 20
        self.WIDTH: int = 1500
        self.HEIGHT: int = 980
        self.window: pygame.Surface = window
        self.ui_manager: UIManager = ui_manager
        self.last_time_in_menu: float = 0
        self.time_before_menu: float = 0.2
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

    def game_loop(self, seed: str|None=None, save_name: str|None=None) -> int:
        is_new_map = True
        exit_code = menus.EXIT
        clock = pygame.time.Clock()
        if not seed:
            seed = None
        map_generator = MapGenerator(seed)
        save_manager = SaveManager()
        if is_new_map:
            map_generator.create_seeds()
        player = Player('base_character', 0, Chunk.HEIGHT, 0, 0, self.window, map_generator, clock, save_manager)
        pygame.key.set_repeat(100, 100)
        loop = True
        print(f'seed: "{map_generator.seed}"')
        need_update = True
        while loop:
            if need_update:
                self.window.fill("#000000", pygame.Rect(0, 0, self.WIDTH, self.HEIGHT))
                player.chunk_manager.display_chunks(player.x, player.y)
                player.display()
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
                        exit_code = menus.EscapeMenu(self.ui_manager).run()
                        self.last_time_in_menu = monotonic()
                        need_update = True
                        if exit_code == menus.EXIT or exit_code == menus.TO_MAIN_MENU:
                            loop = False
                            break
                        elif exit_code == menus.BACK:
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
                need_update = player.place_block(pygame.mouse.get_pos())
            if pressed_mouse_buttons[2]:
                need_update = player.remove_block(pygame.mouse.get_pos())

            need_update = player.update() or need_update
            clock.tick(self.FPS)
        player.save()
        return exit_code

    def run(self) -> None:
        while True:
            main_menu = menus.MainMenu(self.ui_manager)
            exit_code = main_menu.run()
            if exit_code == menus.EXIT:
                break
            elif exit_code == menus.CREATE_GAME:
                create_world_menu = menus.CreateWorldMenu(self.ui_manager)
                exit_code = create_world_menu.run()
                if exit_code == menus.START_GAME:
                    exit_code = self.game_loop(create_world_menu.seed_text_box.get_text())
                    if exit_code == menus.EXIT:
                        break
                    elif exit_code == menus.TO_MAIN_MENU:
                        pass
        pygame.quit()

hud_size = 1 # percentage

game = Game(window, ui_manager)
