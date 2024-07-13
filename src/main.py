import pygame
from blocks import BLOCKS
from items import ITEMS
from player import Player

class Game:
    def __init__(self) -> None:
        self.FPS = 15
        self.WIDTH = 500
        self.HEIGHT = 500
        self.window = None
        self.run()

    def game_loop(self) -> None:
        clock = pygame.time.Clock()
        player = Player(0, 11, 0, 0, self.window)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_exit()
                    return
                elif event.type == pygame.KEYDOWN:
                    ...
            pygame.display.update()
            clock.tick(self.FPS)

    def game_exit(self):
        ...

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
        pygame.quit()


game = Game()
game.run()
