import pygame
from blocks import BLOCKS
from items import ITEMS
from player import Player

class Game:
    def __init__(self) -> None:
        self.FPS = 20
        self.WIDTH = 1500
        self.HEIGHT = 1000
        self.window = None
        self.keys = {
            "mv_left": pygame.K_LEFT, #moves
            "mv_right": pygame.K_RIGHT,
            "inv_1": pygame.K_1, # inventory
            "inv_2": pygame.K_2,
            "inv_3": pygame.K_3,
            "inv_4": pygame.K_4,
            "inv_5": pygame.K_5,
            "inv_6": pygame.K_6,
            "inv_7": pygame.K_7,
            "inv_8": pygame.K_8,
            "inv_9": pygame.K_9,
            "inv_10": pygame.K_0,
        }
        self.run()

    def game_loop(self) -> None:
        clock = pygame.time.Clock()
        player = Player('base_character', 0, 16, 0, 0, self.window)
        player.load_image()
        pygame.key.set_repeat(100, 100)
        loop = True
        while loop:
            self.window.fill("#000000", pygame.Rect(0, 0, self.WIDTH, self.HEIGHT))
            player.chunk_manager.display_chunks(player.x, player.y)
            player.display()
            player.display_hud()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == self.keys["mv_left"]:
                        player.speed_x = -1
                    elif event.key == self.keys["mv_right"]:
                        player.speed_x = 1
                    elif event.key == self.keys["inv_1"]:
                        player.inventory.selected = 0
                    elif event.key == self.keys["inv_2"]:
                        player.inventory.selected = 1
                    elif event.key == self.keys["inv_3"]:
                        player.inventory.selected = 2
                    elif event.key == self.keys["inv_4"]:
                        player.inventory.selected = 3
                    elif event.key == self.keys["inv_5"]:
                        player.inventory.selected = 4
                    elif event.key == self.keys["inv_6"]:
                        player.inventory.selected = 5
                    elif event.key == self.keys["inv_7"]:
                        player.inventory.selected = 6
                    elif event.key == self.keys["inv_8"]:
                        player.inventory.selected = 7
                    elif event.key == self.keys["inv_9"]:
                        player.inventory.selected = 8
                    elif event.key == self.keys["inv_10"]:
                        player.inventory.selected = 9
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                player.place_block(pygame.mouse.get_pos())
            if pressed_mouse_buttons[2]:
                player.remove_block(pygame.mouse.get_pos())

            player.update()
            pygame.display.update()
            clock.tick(self.FPS)
        player.save()

    def run(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        for block in BLOCKS:
            block.load_image()
        for item in ITEMS:
            item.load_image()
        exit = False
        while not exit:
            self.game_loop()
            exit = True
        pygame.quit()


game = Game()
