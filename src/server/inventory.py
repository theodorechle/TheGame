import items
from time import monotonic
from math import ceil
from inventory_interface import InventoryInterface

class Inventory(InventoryInterface):
    def __init__(self, nb_cells: int, cells: list[tuple[items.Item|None, int]]|None=None, classes_names: list[str]|None=None, anchor: str = 'top-left') -> None:
        super().__init__(nb_cells, cells)
        self.nb_cells_by_line = min(10, self._nb_cells)

    def add_element_at_pos(self, element: items.Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
        if 0 > pos or pos >= len(self.cells): return 0
        if self.cells[pos][0] == items.NOTHING: self.cells[pos] = (element, 0)
        elif self.cells[pos][0] != element: return 0
        added_quantity = min(quantity, element.stack_size - self.cells[pos][1])
        self.cells[pos] = (element, self.cells[pos][1] + added_quantity)
        return added_quantity
    
    def add_element(self, element: items.Item, quantity: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at the first free space.
        Returns the quantity effectively added.
        """
        added_quantity: int = 0
        for index in range(len(self.cells)):
            added_quantity = self.add_element_at_pos(element, quantity - added_quantity, index)
            if quantity == added_quantity:
                break
        return added_quantity
    
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item|None, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
        if 0 > pos or pos >= len(self.cells): return (None, 0)
        removed_quantity = min(quantity, self.cells[pos][1])
        cell = (self.cells[pos][0], removed_quantity)
        self.cells[pos] = (self.cells[pos][0], self.cells[pos][1] - removed_quantity)
        if self.cells[pos][1] == 0:
            self.cells[pos] = (items.NOTHING, 0)
        return cell

    def remove_element(self, element: items.Item) -> int:
        """
        Remove all instances of element in the inventory.
        Returns the quantity effectively removed
        """
        removed_quantity: int = 0
        for index in range(len(self.cells)):
            if self.cells[index][0] == element:
                removed_quantity += self.cells[index][1]
                self.cells[index] = (items.NOTHING, 0)
        return removed_quantity

    def get_element_quantity(self, element: items.Item) -> int:
        quantity = 0
        for cell in self.cells:
            if cell[0] != element: continue
            quantity += cell[1]
        return quantity

    def is_present_in_quantity(self, element: items.Item, quantity: int) -> bool:
        """
        Check if the given quantity of the given element is present in the inventory
        """
        for cell in self.cells:
            if cell[0] != element: continue
            quantity -= min(quantity, cell[1])
            if quantity == 0: break
        return quantity == 0

    def remove_quantity(self, element: items.Item, quantity: int) -> int:
        """
        Returns the quantity effectively removed
        """
        removed_quantity = 0
        for index, cell in enumerate(self.cells):
            if cell[0] != element: continue
            removed_quantity += self.remove_element_at_pos(quantity - removed_quantity, index)[1]
            if quantity == removed_quantity: return removed_quantity
        return removed_quantity

    def empty_cell(self, pos: int) -> tuple[items.Item|None, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
        if 0 > pos or pos >= len(self.cells): return (items.NOTHING, 0)
        cell = self.cells[pos]
        self.cells[pos] = (items.NOTHING, 0)
        return cell

    def sort(self) -> None:
        ...
