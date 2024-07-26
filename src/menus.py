from pygame.event import Event
from gui import ui_manager, elements
import pygame
from time import monotonic

EXIT = 0
CREATE_GAME = 1
TO_MAIN_MENU = 2
BACK = 3
START_GAME = 4

class Menu:
    def __init__(self, manager: ui_manager.UIManager) -> None:
        self.ui_manager = manager
        self._loop = True
        self._exit_code = EXIT
        self.time_menu_creation = 0
        self.min_time_before_exit = 0.3 # seconds
        self.elements = []

    def exit(self, code) -> bool:
        if self.time_menu_creation > monotonic() - self.min_time_before_exit:
            return False
        self._loop = False
        self._exit_code = code
        for element in self.elements:
            self.ui_manager.remove_element(element)
        return True

    def exit_menu(self, _) -> None:
        self.exit(BACK)

    def handle_special_events(self, event: pygame.event.Event) -> pygame.event.Event|None:
        """
        This function exists to be overriden
        Get every event and process it.
        Can return the event, in which case it will be processed by the normal run method and the ui manager.
        By default, it will only quit the menu if the window exit cross is pressed
        """
        if event.type == pygame.QUIT:
            self.exit(EXIT)
        return event

    def run(self) -> int:
        while self._loop:
            for event in pygame.event.get():
                event = self.handle_special_events(event)
                if event is None:
                    continue
                self.ui_manager.process_event(event)
                self.ui_manager.update()
            pygame.display.update()
        return self._exit_code

class MainMenu(Menu):
    def __init__(self, manager: ui_manager.UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Create new world', on_click_function=self.create_new_game, start_y=manager.window.get_size()[1] // 4, horizontal_center=True))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_game, start_y=manager.window.get_size()[1] // 4 * 3, horizontal_center=True))
    
    def exit_game(self, _) -> None:
        self.exit(EXIT)

    def create_new_game(self, _) -> None:
        self.exit(CREATE_GAME)

class CreateWorldMenu(Menu):
    def __init__(self, manager: ui_manager.UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.InputTextBox(manager, placeholder_text="World's name", forbidden_chars=['\\', '/', ':', '*', '?', '"', '<', '>', '|'], horizontal_center=True, start_y=400))
        self.elements.append(elements.InputTextBox(manager, placeholder_text='Seed', horizontal_center=True, start_y=600))
        self.elements.append(elements.Button(manager, 'Create', on_click_function=self.start_game, horizontal_center=True, start_y=800))
        self.elements.append(elements.Button(manager, 'Back', on_click_function=self.exit_menu, start_x=100, start_y=100))
        
    def start_game(self, _) -> None:
        self.exit(START_GAME)

class EscapeMenu(Menu):
    def __init__(self, manager: ui_manager.UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Exit to main menu', on_click_function=self.exit_to_main_menu, horizontal_center=True, vertical_center=True))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_menu, start_y=manager.window.get_size()[1] // 4 * 3, horizontal_center=True))
    
    def exit_to_main_menu(self, _) -> None:
        self.exit(TO_MAIN_MENU)
    
    def handle_special_events(self, event: Event) -> Event | None:
        if event.type == pygame.QUIT:
            self.exit(EXIT)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit(BACK)
        return event