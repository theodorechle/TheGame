import pygame
from blocks import BLOCKS
from items import ITEMS
from player import Player

class Game:
    def __init__(self) -> None:
        self.FPS = 2
        self.WIDTH = 1500
        self.HEIGHT = 1000
        self.window = None
        self.run()

    def game_loop(self) -> None:
        clock = pygame.time.Clock()
        player = Player('base_character', 0, 16, 0, 0, self.window)
        player.load_image()
        while True:
            self.window.fill("#000000", pygame.Rect(0, 0, self.WIDTH, self.HEIGHT))
            player.chunk_manager.display_chunks(player.x, player.y)
            player.display()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_exit()
                    return
                elif event.type == pygame.KEYDOWN:
                    ...
            player.x -= 2
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
