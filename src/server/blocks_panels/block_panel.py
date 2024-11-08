from time import monotonic
from typing import Any
from entities.player_interface import PlayerInterface

class BlockPanel():
    def __init__(self, block_data: dict[str, Any], player: PlayerInterface) -> None:
        self.block_data = block_data
        self.player = player
        self.need_update = False
        self.entered_time = monotonic()
        self.min_time_before_exit = 0.3

    # def process_event(self, event: pygame.event.Event, exit_key: int) -> bool:
    #     """
    #     Return True if the player exited the menu, False else
    #     """
    #     # can be modified to forbid quitting, for example writing in a textbox
    #     if self.entered_time + self.min_time_before_exit < monotonic():
    #         if event.type == pygame.KEYDOWN:
    #             if event.key == exit_key: return True
    #             elif event.key == pygame.K_ESCAPE: return True
    #         elif event.type == pygame.MOUSEBUTTONDOWN:
    #             if event.button == exit_key: return True
    #     self._ui_manager.process_event(event)
    #     return False
    
    # def update(self) -> bool:
    #     need_update = self._ui_manager.update() or self.need_update
    #     self.need_update = False
    #     return need_update
    
    # def display(self, clear: bool=True) -> None:
    #     self._ui_manager.display(clear)
    
    def close(self) -> None:
        ...