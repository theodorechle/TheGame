from abc import abstractmethod, ABCMeta
import items

class InventoryInterface(metaclass=ABCMeta):
    def __init__(self, nb_cells: int) -> None:
        self._nb_cells: int = nb_cells
        self.cells: list[tuple[items.Item|None, int]] = [(items.NOTHING, 0) for _ in range(self._nb_cells)] # list of list with items and quantities

    def set_cells(self, cells) -> None:
        self.cells: list[tuple[items.Item|None, int]] = [(items.REVERSED_ITEMS_DICT[item], qty) for item, qty in cells] # list of list with items and quantities
    
    def get_nb_cells(self) -> int:
        return self._nb_cells
    
    @abstractmethod
    def get_element_quantity(self, element: items.Item) -> int:
        pass
    
    @abstractmethod
    def is_present_in_quantity(self, element: items.Item, quantity: int) -> bool:
        pass

    @abstractmethod
    def sort(self) -> None:
        pass
