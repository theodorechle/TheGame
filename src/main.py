import pygame
from blocks import BLOCKS
from items import ITEMS
from player import Player

class Game:
    def __init__(self) -> None:
        self.FPS = 5
        self.WIDTH = 1500
        self.HEIGHT = 1000
        self.window = None
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.speed_x = -1
                    elif event.key == pygame.K_RIGHT:
                        player.speed_x = 1
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
