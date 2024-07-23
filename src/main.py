import pygame
from blocks import BLOCKS
from items import ITEMS
from player import Player
from map_generation import MapGenerator
from chunk_manager import Chunk
from random import randint

class Game:
    def __init__(self) -> None:
        self.FPS = 20
        self.WIDTH = 1500
        self.HEIGHT = 1000
        self.window = None
        self.keys = {
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
        self.pressed_keys = {
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

    def game_loop(self) -> None:
        is_new_map = True
        clock = pygame.time.Clock()
        map_generator = MapGenerator()
        if is_new_map:
            map_generator.create_seeds()
        player = Player('base_character', 0, Chunk.HEIGHT, 0, 0, self.window, map_generator)
        player.load_image()
        pygame.key.set_repeat(100, 100)
        loop = True
        print(f'seed: {map_generator.seed}')
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
                    break
                elif event.type == pygame.KEYDOWN:
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
                    elif event.key == self.keys['open_inv']:
                        self.pressed_keys['open_inv'] = False
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
                player.inventory.display_all = not player.inventory.display_all
            for i in range(10):
                if self.pressed_keys[f'inv_{i}']:
                    player.inventory.selected = i
                    need_update = True

            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                player.place_block(pygame.mouse.get_pos())
                need_update = True
            if pressed_mouse_buttons[2]:
                player.remove_block(pygame.mouse.get_pos())
                need_update = True

            need_update = need_update or player.update()
            clock.tick(self.FPS)
        player.save()

    def run(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        for block in BLOCKS:
            block.load_image()
        for item in ITEMS:
            item.load_image()
        exit = False
        while not exit:
            self.game_loop()
            exit = True
        pygame.quit()

hud_size = 1 # percentage

game = Game()
