from pygame import Surface
from inventory import Inventory
from items import Item

class FurnaceInventory(Inventory):
    def __init__(self, nb_cells: int, window: Surface, cells: list[tuple[Item | None, int]] | None = None) -> None:
        super().__init__(nb_cells, window, cells)
        self.burning_item: tuple[Item, int]|None = None

    def set_burning_item(self, item: tuple[Item, int]|None) -> None:
        self.burning_item = item