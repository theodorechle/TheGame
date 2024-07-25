from gui import ui_manager, elements
import pygame

EXIT = 0
NEW_GAME = 1

class MainMenu:
    def __init__(self, manager: ui_manager.UIManager) -> None:
        self.ui_manager = manager
        elements.Button(manager, 'Create new world', on_click_function=self.create_new_game, start_y=manager.window.get_size()[1] // 4, horizontal_center=True)
        elements.Button(manager, 'QUIT', on_click_function=self.quit, start_y=manager.window.get_size()[1] // 4 * 3, horizontal_center=True)
        self.loop = True
        self.exit_code = EXIT
        
    def create_new_game(self, _) -> None:
        self.loop = False
        self.exit_code = NEW_GAME
    
    def quit(self, _) -> None:
        self.loop = False
        self.exit_code = EXIT

    def run(self) -> None:
        while self.loop:
            for event in pygame.event.get():
                self.ui_manager.process_event(event)
                self.ui_manager.update()
            pygame.display.update()
        return self.exit_code
