from pygame import Surface
from inventory import Inventory
from items import Item

class FurnaceInventory(Inventory):
    def __init__(self, start_x: int, start_y: int, nb_cells: int, window: Surface, cells: list[tuple[Item | None, int]] | None = None) -> None:
        super().__init__(nb_cells, window, cells)
        self.main_bar_start_pos = (start_x, start_y)
        self.burning_item: tuple[Item, int]|None = None

    def set_burning_item(self, item: tuple[Item, int]|None) -> None:
        self.burning_item = item
    
