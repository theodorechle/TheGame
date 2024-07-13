import pygame


class Game:
    def __init__(self) -> None:
        self.FPS = 15
        self.WIDTH = 1500
        self.HEIGHT = 500
        self.run()

    def game_loop(self) -> None:
        clock = pygame.time.Clock()
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
        pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        exit = False
        while not exit:
            self.game_loop()
        pygame.quit()


game = Game()
