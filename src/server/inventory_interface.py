from abc import abstractmethod, ABCMeta
import items

class InventoryInterface(metaclass=ABCMeta):
    def __init__(self, nb_cells: int, cells: list[tuple[int, int]]|None=None) -> None:
        self._nb_cells: int = nb_cells
        if cells:
            self.cells: list[tuple[int, int]] = cells.copy()
        else:
            self.cells: list[tuple[int, int]] = [(-1, 0) for _ in range(self._nb_cells)] # list of list with items and quantities

    
    @abstractmethod
    def add_element_at_pos(self, element: items.Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
    
    @abstractmethod
    def add_element(self, element: items.Item, quantity: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at the first free space.
        Returns the quantity effectively added.
        """
    
    @abstractmethod
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item|None, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """

    @abstractmethod
    def remove_element(self, element: items.Item) -> int:
        """
        Remove all instances of element in the inventory.
        Returns the quantity effectively removed
        """
    
    @abstractmethod
    def get_element_quantity(self, element: items.Item) -> int:
        pass
    
    @abstractmethod
    def is_present_in_quantity(self, element: items.Item, quantity: int) -> bool:
        pass

    @abstractmethod
    def remove_quantity(self, element: items.Item, quantity: int) -> int:
        pass

    @abstractmethod
    def empty_cell(self, pos: int) -> tuple[items.Item|None, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
    
    @abstractmethod
    def sort(self) -> None:
        pass
