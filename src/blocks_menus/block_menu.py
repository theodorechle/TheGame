import pygame
from gui.ui_manager import UIManager
from gui.ui_element import UIElement
from time import monotonic
import os

BLOCKS_MENUS_THEMES_PATH = os.path.join('src', 'resources', 'gui_themes', 'blocks_menus')

class BlockMenu():
    def __init__(self, window: pygame.Surface, *ui_manager_parameters) -> None:
        self.window = window
        self._ui_manager = UIManager(window, *ui_manager_parameters)
        self._elements: list[UIElement] = []
        self.need_update = False
        self.entered_time = monotonic()
        self.min_time_before_exit = 0.3

    def process_event(self, event: pygame.event.Event, exit_key: int) -> bool:
        """
        Return True if the player exited the menu, False else
        """
        # can be modified to forbid quitting, for example writing in a textbox
        if self.entered_time + self.min_time_before_exit < monotonic():
            if event.type == pygame.KEYDOWN:
                if event.key == exit_key: return True
                elif event.key == pygame.K_ESCAPE: return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == exit_key: return True
        self._ui_manager.process_event(event)
        return False
    
    def update(self) -> bool:
        need_update = self._ui_manager.update() or self.need_update
        self.need_update = False
        return need_update