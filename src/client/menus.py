from pygame.event import Event
from gui.ui_manager import UIManager
from gui import elements
from gui.ui_element import UIElement
import pygame
from time import monotonic
import os
from module_infos import RESOURCES_PATH
from server_connection import ServerConnection
import asyncio

EXIT = 0
CREATE_GAME = 1
TO_MAIN_MENU = 2
BACK = 3
START_GAME = 4
SETTINGS = 5
LOAD_SAVE = 6

class Menu:
    FPS = 20
    THEMES_PATH = os.path.join(RESOURCES_PATH, 'gui_themes', 'menus_themes')
    def __init__(self, window: pygame.Surface, server: ServerConnection) -> None:
        self.ui_manager = UIManager(window)
        self.server = server
        self._loop = True
        self._exit_code = EXIT
        self.time_menu_creation = monotonic()
        self.min_time_before_exit = 0.2 # seconds
        self._elements: list[UIElement] = []

    def exit(self, code: int) -> bool:
        if self.time_menu_creation > monotonic() - self.min_time_before_exit:
            return False
        self._loop = False
        self._exit_code = code
        self.ui_manager.delete_all_elements()
        return True

    def exit_menu(self, _: UIElement) -> None:
        self.exit(BACK)

    def handle_special_events(self, event: pygame.event.Event) -> pygame.event.Event|None:
        """
        Get every event and process it.
        Can return the event, in which case it will be processed by the normal run method and the ui manager.
        By default, it will only quit the menu if the window exit cross is pressed (send an EXIT code)
        and when the escape button is pressed (send a BACK code)
        """
        if event.type == pygame.QUIT:
            self.exit(EXIT)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit(BACK)
        return event

    def run_functions_start_loop(self) -> None:
        """
        Designed to be overriden.
        Allow functions to run at the start of the loop, before events processing.
        """
        pass

    def run_functions_end_loop(self) -> None:
        """
        Designed to be overriden.
        Allow functions to run at the end of the loop, after events processing and before ui_manager and display update.
        """
        pass

    def run(self) -> int:
        clock = pygame.time.Clock()
        while self._loop:
            self.run_functions_start_loop()
            for event in pygame.event.get():
                event = self.handle_special_events(event)
                if event is None:
                    continue
                self.ui_manager.process_event(event)
            self.run_functions_end_loop()
            self.ui_manager.update()
            self.ui_manager.display()
            pygame.display.update()
            clock.tick(self.FPS)
        pygame.event.clear()
        return self._exit_code

class MainMenu(Menu):
    def __init__(self, window: pygame.Surface, server: ServerConnection) -> None:
        super().__init__(window, server)
        self._elements.append(elements.TextButton(self.ui_manager, 'Create new world', on_click_function=self.create_new_game, y="-15%", anchor='center'))
        self._elements.append(elements.TextButton(self.ui_manager, 'Load save', on_click_function=self.load_save, anchor='center'))
        self._elements.append(elements.TextButton(self.ui_manager, 'QUIT', on_click_function=self.exit_game, y="15%", anchor='center'))
    
    def exit_game(self, _: UIElement) -> None:
        self.exit(EXIT)

    def load_save(self, _: UIElement) -> None:
        self.exit(LOAD_SAVE)

    def create_new_game(self, _: UIElement) -> None:
        self.exit(CREATE_GAME)
    
    def handle_special_events(self, event: Event) -> Event | None:
        if event.type == pygame.QUIT:
            self.exit(EXIT)
        return event

class CreateWorldMenu(Menu):
    def __init__(self, window: pygame.Surface, server: ServerConnection) -> None:
        super().__init__(window, server)
        self.world_name_text_box: elements.InputTextBox = elements.InputTextBox(self.ui_manager, placeholder_text="World's name", forbidden_chars=['\\', '/', ':', '*', '?', '"', '<', '>', '|'], anchor='top', y=400)
        self._elements.append(self.world_name_text_box)
        self.seed_text_box: elements.InputTextBox = elements.InputTextBox(self.ui_manager, placeholder_text='Seed', anchor='top', y=600)
        self._elements.append(self.seed_text_box)
        self._elements.append(elements.TextButton(self.ui_manager, 'Create', on_click_function=self.start_game, anchor='top', y=800))
        self._elements.append(elements.TextButton(self.ui_manager, 'Back', on_click_function=self.exit_menu, x=100, y=100))
    
    def start_game(self, _: UIElement) -> None:
        text = self.world_name_text_box.get_text()
        if text and not text.isspace():
            self.exit(START_GAME)

class EscapeMenu(Menu):
    def __init__(self, window: pygame.Surface, server: ServerConnection) -> None:
        super().__init__(window, server)
        self._elements.append(elements.TextButton(self.ui_manager, 'Exit to main menu', on_click_function=self.exit_to_main_menu, anchor='center'))
        self._elements.append(elements.TextButton(self.ui_manager, 'QUIT', on_click_function=self.exit_menu, x='-2%', anchor='right'))
        self._elements.append(elements.TextButton(self.ui_manager, 'SETTINGS', on_click_function=self.to_settings, x='2%', y='-25%', anchor='left'))
    
    def exit_to_main_menu(self, _: UIElement) -> None:
        self.exit(TO_MAIN_MENU)
    
    def to_settings(self, _: UIElement) -> None:
        self.exit(SETTINGS)

class SettingsMenu(Menu):
    def __init__(self, window: pygame.Surface, server: ServerConnection, nb_chunks_loaded: int=0, zoom: int=30) -> None:
        super().__init__(window, server)
        # loaded chunks
        self._elements.append(elements.Label(self.ui_manager, 'Nb chunks loaded on each side', y="-30%", anchor='center'))
        self.slider_nb_chunks = elements.Slider(self.ui_manager, 1, 25, 1, y="-20%", anchor='center')
        self.slider_nb_chunks.set_value(nb_chunks_loaded)
        self._elements.append(self.slider_nb_chunks)
        self.label_nb_chunks = elements.Label(self.ui_manager, y='-15%', anchor='center', width=30)
        self._elements.append(self.label_nb_chunks)
        # zoom
        self._elements.append(elements.Label(self.ui_manager, 'Zoom', y="10%", anchor='center'))
        self.slider_zoom = elements.Slider(self.ui_manager, 1, 40, 1, y="20%", anchor='center')
        self.slider_zoom.set_value(zoom)
        self._elements.append(self.slider_nb_chunks)
        self.label_zoom = elements.Label(self.ui_manager, y="25%", anchor='center', width=30)
        self._elements.append(self.label_nb_chunks)
        self._elements.append(elements.TextButton(self.ui_manager, 'QUIT', on_click_function=self.exit_menu, x='-2%', anchor='right'))

    def run_functions_end_loop(self) -> None:
        self.label_nb_chunks.set_text(str(self.slider_nb_chunks.get_value()))
        self.label_zoom.set_text(str(self.slider_zoom.get_value()))

class LoadSaveMenu(Menu):
    def __init__(self, window: pygame.Surface, server: ServerConnection) -> None:
        super().__init__(window, server)
        self.ui_manager.update_theme(os.path.join(self.THEMES_PATH, 'load_save_menu_theme.json'))
        self.saves_list = elements.ItemList(self.ui_manager, height="80%", anchor='top', y='2%', width='50%', items_classes_names=['item-list-childs'])
        self._elements.append(self.saves_list)
        options_container = elements.Container(self.ui_manager, x='-15%', anchor='right', height='8%', classes_names=['options-container'])
        self._elements.append(options_container)
        load_button = elements.TextButton(self.ui_manager, 'Load', self.load_save, anchor='top')
        self._elements.append(load_button)
        delete_button = elements.TextButton(self.ui_manager, 'Delete save', self.delete_save, anchor='bottom', classes_names=['delete-save-button'])
        self._elements.append(delete_button)
        options_container.add_element(load_button)
        options_container.add_element(delete_button)
        self._elements.append(elements.TextButton(self.ui_manager, 'QUIT', self.exit_menu, anchor='bottom', y='-10%'))
        asyncio.run(self.add_saves())
    
    async def add_saves(self) -> None:
        await self.server.send_json({
            'method': 'GET',
            'data': {
                'type': 'saves-list'
            }
        })
        saves = await self.server.receive_msg()
        if not saves or saves['status'] == self.server.WRONG_REQUEST: return
        self.saves_list.add_elements(saves['data']['saves'])

    def load_save(self, _: UIElement) -> None:
        selected = self.saves_list.child_selected
        if selected is None: return
        self.exit(START_GAME)
    
    def delete_save(self, _: UIElement) -> None:
        selected = self.saves_list.child_selected
        if selected is None: return
        data = self.server.send_json({
            'method': 'DELETE',
            'data': {
                'type': 'save',
                'value': selected.get_text()
            }
        })
        if data['status'] != self.server.VALID_REQUEST: return
        self.saves_list.remove_element(selected)
