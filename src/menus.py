from gui import ui_manager, elements
import pygame

EXIT = 0
NEW_GAME = 1
TO_MAIN_MENU = 2

class Menu:
    def __init__(self, manager: ui_manager.UIManager) -> None:
        self.ui_manager = manager
        self.loop = True
        self.exit_code = EXIT
        self.elements = []

    def exit(self, code) -> None:
        self.loop = False
        self.exit_code = code
        for element in self.elements:
            self.ui_manager.remove_element(element)

    def run(self) -> None:
        while self.loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit(EXIT)
                    break
                self.ui_manager.process_event(event)
                self.ui_manager.update()
            pygame.display.update()
        return self.exit_code

class MainMenu(Menu):
    def __init__(self, manager: ui_manager.UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Create new world', on_click_function=self.create_new_game, start_y=manager.window.get_size()[1] // 4, horizontal_center=True))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_menu, start_y=manager.window.get_size()[1] // 4 * 3, horizontal_center=True))
        
    def create_new_game(self, _) -> None:
        self.exit(NEW_GAME)
    
    def exit_menu(self, _) -> None:
        self.exit(EXIT)

class EscapeMenu(Menu):
    def __init__(self, manager: ui_manager.UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Exit to main menu', on_click_function=self.exit_to_main_menu, horizontal_center=True, vertical_center=True))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_menu, start_y=manager.window.get_size()[1] // 4 * 3, horizontal_center=True))
    
    def exit_menu(self, _) -> None:
        self.exit(EXIT)
    
    def exit_to_main_menu(self, _) -> None:
        self.exit(TO_MAIN_MENU)