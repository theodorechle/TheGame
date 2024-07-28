from pygame.event import Event
from gui.ui_manager import UIManager
from gui import elements
from gui.ui_element import UIElement
import pygame
from time import monotonic

EXIT = 0
CREATE_GAME = 1
TO_MAIN_MENU = 2
BACK = 3
START_GAME = 4

class Menu:
    def __init__(self, manager: UIManager) -> None:
        self.ui_manager = manager
        self._loop = True
        self._exit_code = EXIT
        self.time_menu_creation = 0
        self.min_time_before_exit = 0.3 # seconds
        self.elements: list[UIElement] = []

    def exit(self, code: int) -> bool:
        if self.time_menu_creation > monotonic() - self.min_time_before_exit:
            return False
        self._loop = False
        self._exit_code = code
        self.ui_manager.clear_elements_list()
        return True

    def exit_menu(self, _: UIElement) -> None:
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
    def __init__(self, manager: UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Create new world', on_click_function=self.create_new_game, y=-manager.window.get_size()[1] // 4, anchor='center'))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_game, y=manager.window.get_size()[1] // 4, anchor='center'))
    
    def exit_game(self, _: UIElement) -> None:
        self.exit(EXIT)

    def create_new_game(self, _: UIElement) -> None:
        self.exit(CREATE_GAME)

class CreateWorldMenu(Menu):
    def __init__(self, manager: UIManager) -> None:
        super().__init__(manager)
        self.world_name_text_box: elements.InputTextBox = elements.InputTextBox(manager, placeholder_text="World's name", forbidden_chars=['\\', '/', ':', '*', '?', '"', '<', '>', '|'], anchor='top', y=400)
        self.elements.append(self.world_name_text_box)
        self.seed_text_box: elements.InputTextBox = elements.InputTextBox(manager, placeholder_text='Seed', anchor='top', y=600)
        self.elements.append(self.seed_text_box)
        self.elements.append(elements.Button(manager, 'Create', on_click_function=self.start_game, anchor='top', y=800))
        self.elements.append(elements.Button(manager, 'Back', on_click_function=self.exit_menu, x=100, y=100))
    
    def start_game(self, _: UIElement) -> None:
        self.exit(START_GAME)

class EscapeMenu(Menu):
    def __init__(self, manager: UIManager) -> None:
        super().__init__(manager)
        self.elements.append(elements.Button(manager, 'Exit to main menu', on_click_function=self.exit_to_main_menu, anchor='center'))
        self.elements.append(elements.Button(manager, 'QUIT', on_click_function=self.exit_menu, y=manager.window.get_size()[1] // 4, anchor='center'))
    
    def exit_to_main_menu(self, _: UIElement) -> None:
        self.exit(TO_MAIN_MENU)
    
    def handle_special_events(self, event: Event) -> Event | None:
        if event.type == pygame.QUIT:
            self.exit(EXIT)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit(BACK)
        return event