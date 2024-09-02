import sys
from module_infos import GUI_PATH
sys.path.append(GUI_PATH)

import menus
import pygame
pygame.init()
WIDTH = 1500
HEIGHT = 980
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

from server_connection import ServerConnection
from gui.ui_manager import UIManager
from gui import elements
from map_chunk import Chunk
import items
from player import Player

class Client:
    def __init__(self, window) -> None:
        self.exit = False
        self.server = ServerConnection('127.0.0.1', 12345)

        # UI
        self.window = window
        self._ui_manager = UIManager(self.window)

        self.run_menus()

    def run_menus(self) -> None:
        while True:
            exit_code = menus.MainMenu(self.window, self.server).run()
            if exit_code == menus.EXIT:
                self.exit = True
                break
            elif exit_code == menus.CREATE_GAME:
                create_world_menu = menus.CreateWorldMenu(self.window, self.server)
                exit_code = create_world_menu.run()
                if exit_code == menus.BACK:
                    continue
                save_name = create_world_menu.world_name_text_box.get_text().rstrip()
                seed = create_world_menu.seed_text_box.get_text()
                if not seed:
                    seed = None
                self.server.send_json({
                    'method': 'GET',
                    'data': {
                        'type': 'create-world',
                        'seed': seed,
                        'save': save_name
                    }
                })
                player = Player('base_character', 0, Chunk.HEIGHT, 0, 0, False, self._ui_manager)
                # nexts lines are for testing purpose only
                player.hot_bar_inventory.add_element(items.WORKBENCH, 5)
                player.hot_bar_inventory.add_element(items.FURNACE, 5)
            elif exit_code == menus.LOAD_SAVE:
                exit_code = menus.LoadSaveMenu(self.window, self.server).run()
                if exit_code == menus.BACK:
                    continue

    def stop_client(self, _: elements.TextButton) -> None:
        self.exit = True

    def run(self) -> None:
        while not self.exit:
            self.update()
            self.display()

    def update(self) -> None:
        for event in pygame.event.get():
            self._ui_manager.process_event(event)
        self._ui_manager.update()

    def display(self) -> None:
        self._ui_manager.display()
        pygame.display.update()
client = Client(window)
client.run()