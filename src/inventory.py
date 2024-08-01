import pygame
import items
from time import monotonic


class Inventory:
    def __init__(self, nb_cells: int, window: pygame.Surface) -> None:
        self._nb_cells = nb_cells
        self._cells: list[tuple[items.Item|None, int]] = [(items.NOTHING, 0) for _ in range(self._nb_cells)] # list of list with items and quantities
        self.window = window
        self.cell_size = 40
        self.nb_cells_by_line = 10
        self.cells_borders_size = 2
        self.blocks_qty_font_name = ""
        self.blocks_qty_font_size = 20
        self.block_qty_font = pygame.font.SysFont(self.blocks_qty_font_name, self.blocks_qty_font_size)
        self.selected = 0
        self._display_all = False
        self.main_bar_start_pos = (self.window.get_size()[0] // 2 - self.cell_size * self.nb_cells_by_line // 2, self.window.get_size()[1] - self.cell_size)
        self.complete_inventory_start_pos = (self.window.get_size()[0] // 2 - self.cell_size * self.nb_cells_by_line // 2, self.window.get_size()[1] // 2 - self.cell_size * (self._nb_cells // self.nb_cells_by_line - 1) // 2)
        # item, quantity
        self._current_clicked_item: tuple[items.Item|None, int] = (items.NOTHING, 0)
        self._clicked_item_init_pos = -1
        self._last_time_clicked = 0
        self._last_time_toggled = 0
        self.time_before_toggle = 0.2
        self.time_before_click = 0.2
    
    def add_element_at_pos(self, element: items.Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
        if 0 > pos or pos >= len(self._cells): return 0
        if self._cells[pos][0] == items.NOTHING: self._cells[pos] = (element, 0)
        elif self._cells[pos][0] != element: return 0
        added_quantity = min(quantity, element.stack_size - self._cells[pos][1])
        self._cells[pos] = (element, self._cells[pos][1] + added_quantity)
        return added_quantity
    
    def add_element(self, element: items.Item, quantity: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at the first free space.
        Returns the quantity effectively added.
        """
        added_quantity: int = 0
        for index in range(len(self._cells)):
            added_quantity = self.add_element_at_pos(element, quantity - added_quantity, index)
            if quantity == added_quantity:
                break
        return added_quantity
    
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item|None, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
        if 0 > pos or pos >= len(self._cells): return (None, 0)
        removed_quantity = min(quantity, self._cells[pos][1])
        cell = (self._cells[pos][0], removed_quantity)
        self._cells[pos] = (self._cells[pos][0], self._cells[pos][1] - removed_quantity)
        if self._cells[pos][1] == 0:
            self._cells[pos] = (items.NOTHING, 0)
        return cell

    def remove_element(self, element: items.Item) -> int:
        """
        Remove all instances of element in the inventory.
        Returns the quantity effectively removed
        """
        removed_quantity: int = 0
        for index in range(len(self._cells)):
            if self._cells[index][0] == element:
                removed_quantity += self._cells[index][1]
                self._cells[index] = (items.NOTHING, 0)
        return removed_quantity

    def empty_cell(self, pos: int) -> tuple[items.Item|None, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
        if 0 > pos or pos >= len(self._cells): return (items.NOTHING, 0)
        cell = self._cells[pos]
        self._cells[pos] = (items.NOTHING, 0)
        return cell

    def sort(self) -> None:
        ...

    def display(self) -> None:
        self.display_main_bar()
        if self._display_all:
            for index in range(self.nb_cells_by_line, len(self._cells)):
                x, y = self.complete_inventory_start_pos[0] + (index % self.nb_cells_by_line) * self.cell_size, self.complete_inventory_start_pos[1] + (index // self.nb_cells_by_line - 1) * self.cell_size
                self._display_cell(x, y, False)
                block, qty = self._cells[index]
                if block is None: continue
                self._display_item(x, y, block, qty)
        if self._current_clicked_item[0] is not None:
            self._display_item(*pygame.mouse.get_pos(), self._current_clicked_item[0], self._current_clicked_item[1])
    
    def display_main_bar(self) -> None:
        start_x = self.main_bar_start_pos[0]
        start_y = self.main_bar_start_pos[1]
        for index in range(self.nb_cells_by_line):
            x = start_x + index * self.cell_size
            self._display_cell(x, start_y, self.selected == index)
            if index >= len(self._cells): continue
            block, qty = self._cells[index]
            if block is None: continue
            self._display_item(x, start_y, block, qty)

    def _display_cell(self, x: int, y: int, selected: bool) -> None:
        border_size = self.cells_borders_size * (1 + selected)
        pygame.draw.rect(self.window, "#dddddd", pygame.Rect(x, y, self.cell_size, self.cell_size))
        pygame.draw.rect(self.window, "#aaaaaa", pygame.Rect(x, y, self.cell_size, self.cell_size), border_size)

    def _display_item(self, x: int, y: int, item: items.Item, qty: int) -> None:
        item_img_start = (self.cell_size - items.Item.ITEM_SIZE) // 2
        self.window.blit(item.image, (x + item_img_start, y + item_img_start))
        str_qty = str(qty)
        qty_render_size = self.block_qty_font.size(str_qty)
        self.window.blit(self.block_qty_font
                            .render(str_qty, True, "#000000"), (x + self.cell_size - qty_render_size[0], y + self.cell_size - qty_render_size[1]))

    def toggle_inventory(self) -> bool:
        """
        Returns whether it needs a screen update or not
        """
        if self._last_time_toggled > monotonic() - self.time_before_toggle: return False
        self._display_all = not self._display_all 
        self._last_time_toggled = monotonic()
        return True
    
    def have_clicked_item(self) -> bool:
        return self._clicked_item_init_pos != -1

    def click_cell(self, x: int, y: int) -> bool:
        if self._last_time_clicked > monotonic() - self.time_before_click: return False
        if self.main_bar_start_pos[1] <= y <= self.main_bar_start_pos[1] + self.cell_size: # main bar
            if self.main_bar_start_pos[0] <= x <= self.main_bar_start_pos[0] + self.cell_size * 10:
                x -= self.main_bar_start_pos[0]
                x //= self.cell_size
                index = x
            else: return False
        elif self.complete_inventory_start_pos[1] <= y <= self.complete_inventory_start_pos[1] + self.cell_size * (self._nb_cells // self.nb_cells_by_line + 1): # all inventory
            if self.complete_inventory_start_pos[0] <= x <= self.complete_inventory_start_pos[0] + self.cell_size * self.nb_cells_by_line:
                x -= self.complete_inventory_start_pos[0]
                x //= self.cell_size
                y -= self.complete_inventory_start_pos[1]
                y //= self.cell_size
                y += 1
                index = y * self.nb_cells_by_line + x
            else: return False
        else:
            return False
        if index >= self._nb_cells: return False
        if self._current_clicked_item[0] is None:
            item, qty = self.empty_cell(index)
            if item != items.NOTHING:
                self._clicked_item_init_pos = index
                self._current_clicked_item = (item, qty)
        else:
            removed_qty = self.add_element_at_pos(self._current_clicked_item[0], self._current_clicked_item[1], index)
            self._current_clicked_item = (self._current_clicked_item[0], self._current_clicked_item[1] - removed_qty)
            if self._current_clicked_item[1] == 0:
                self._current_clicked_item = (items.NOTHING, 0)
                self._clicked_item_init_pos = -1
        self._last_time_clicked = monotonic()
        return True
