import sys
from module_infos import GUI_PATH
sys.path.append(GUI_PATH)

import menus
import pygame
from server_connection import ServerConnection
from gui.ui_manager import UIManager
from gui import elements

class Client:
    def __init__(self) -> None:
        self.exit = False
        self.server = ServerConnection('127.0.0.1', 12345)

        # UI
        pygame.init()

        WIDTH = 1500
        HEIGHT = 980
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self._ui_manager = UIManager(self.window)

        self.run_menus()

    def run_menus(self) -> None:
        while True:
            exit_code = menus.MainMenu(self.window, self.server).run()
            if exit_code == menus.EXIT:
                self.exit = True
                break
            elif exit_code == menus.CREATE_GAME:
                exit_code = menus.CreateWorldMenu(self.window, self.server).run()
                if exit_code == menus.BACK:
                    continue
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
client = Client()
client.run()