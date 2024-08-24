from abc import abstractmethod, ABCMeta
from items import Item

class InventoryInterface(metaclass=ABCMeta):
    @abstractmethod
    def add_element_at_pos(self, element: Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
    
    @abstractmethod
    def add_element(self, element: Item, quantity: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at the first free space.
        Returns the quantity effectively added.
        """
    
    @abstractmethod
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[Item|None, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
    
    @abstractmethod
    def remove_element(self, element: Item) -> int:
        """
        Remove all instances of element in the inventory.
        Returns the quantity effectively removed
        """

    @abstractmethod
    def empty_cell(self, pos: int) -> tuple[Item|None, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
    
    @abstractmethod
    def sort(self) -> None:
        pass
    
    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def display_main_bar(self) -> None:
        pass

    @abstractmethod
    def _display_cell(self, x: int, y: int, selected: bool) -> None:
        pass

    @abstractmethod
    def _display_item(self, x: int, y: int, item: Item, qty: int) -> None:
        pass

    @abstractmethod
    def toggle_inventory(self) -> bool:
        pass

    @abstractmethod
    def have_clicked_item(self) -> bool:
        pass

    @abstractmethod
    def click_cell(self, x: int, y: int) -> bool:
        pass

    @abstractmethod
    def place_clicked_item(self, pos: int) -> None:
        pass

    @abstractmethod
    def place_back_clicked_item(self) -> None:
        pass
