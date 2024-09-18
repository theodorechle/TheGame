import blocks
from entity import Entity
from inventory import Inventory
from player_interface import PlayerInterface
import items
from time import monotonic
from chunk_manager import ChunkManager
from typing import Any

class Player(Entity, PlayerInterface):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, chunk_manager: ChunkManager, main_inventory_cells: list[tuple[items.Item|None, int]]|None=None, hot_bar_inventory_cells: list[tuple[items.Item|None, int]]|None=None, images_name: str="") -> None:
        PlayerInterface.__init__(self)
        self.interaction_range: int = 1 # doesn't work

        Entity.__init__(self, name, x, y, speed_x, speed_y, direction, 1, 2, chunk_manager, 'persos', True, images_name=images_name)
        self.inventory_size: int = 50
        self.main_inventory: Inventory = Inventory(self.inventory_size - 10, main_inventory_cells, classes_names=['main-inventory'], anchor='center')
        self.hot_bar_inventory: Inventory = Inventory(10, hot_bar_inventory_cells, classes_names=['hot-bar-inventory'], anchor='bottom')
        self.hot_bar_inventory.set_selected_cell(0, 0)
        self.set_player_edges_pos()

    def update(self, delta_t: float) -> bool:
        self.item_clicked_last_frame = False
        need_update = super().update(delta_t)
        # self.chunk_manager.update(self.x)
        return need_update

    def save(self) -> None:
        self.chunk_manager.save()
    
    def _get_relative_pos(self, x: int, y: int) -> tuple[int, int]:
        x = (x - self.window.get_size()[0] // 2 + blocks.Block.BLOCK_SIZE // 2) // blocks.Block.BLOCK_SIZE
        y = -(y - self.window.get_size()[1] // 2) // blocks.Block.BLOCK_SIZE
        return x, y
    
    def _is_interactable(self, x: int, y: int) -> bool:
        if self.bottom_player_pos-self.interaction_range + 1 <= y < self.top_player_pos + self.interaction_range - 1: # left or right
            if self.direction:
                return x == self.left_player_pos - self.interaction_range
            else:
                return x == self.right_player_pos + self.interaction_range
        elif y == self.bottom_player_pos-self.interaction_range or y == self.top_player_pos + self.interaction_range - 1: # down or up
            if self.left_player_pos - self.interaction_range + 1 <= x < self.right_player_pos + self.interaction_range:
                return True
            # edges
            elif self.left_player_pos - self.interaction_range == x:
                if y == self.bottom_player_pos-self.interaction_range: # down-left
                    return self.chunk_manager.get_block(self.x + x, self.y + y + self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + x + self.interaction_range, self.y + y) in blocks.TRAVERSABLE_BLOCKS
                else: # up-left
                    return self.chunk_manager.get_block(self.x + x, self.y + y - self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + x + self.interaction_range, self.y + y) in blocks.TRAVERSABLE_BLOCKS
            elif x == self.entity_size[0] // 2 + self.interaction_range:
                if y == self.bottom_player_pos-self.interaction_range: # down-right
                    return self.chunk_manager.get_block(self.x + x, self.y + y + self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + x - self.interaction_range, self.y + y) in blocks.TRAVERSABLE_BLOCKS
                else: # up-right
                    return self.chunk_manager.get_block(self.x + x, self.y + y - self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + x - self.interaction_range, self.y + y) in blocks.TRAVERSABLE_BLOCKS
        return False

    def _is_surrounded_by_block(self, x: int, y: int) -> bool:
        return (self.chunk_manager.get_block(x + 1, y) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x, y + 1) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x - 1, y) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x, y - 1) not in blocks.TRAVERSABLE_BLOCKS)

    def drag_item_in_inventory(self, inventory: Inventory, index: int=-1) -> bool:
        if self._last_time_clicked + self.min_time_before_click > monotonic(): return
        if index == -1:
            index = inventory.get_clicked_cell()
        if index != -1:
            if self._current_dragged_item[0] == items.NOTHING:
                if inventory.cells[index][0] is not items.NOTHING:
                    self._dragged_item_element = inventory.inventory_table.get_element_by_index(index).__copy__()
                    self._dragged_item_element.classes_names.append('dragged-item')
                    self._ui_manager.update_element_theme(self._dragged_item_element)
                    self._dragged_item_element.update_element()
                    item = inventory.empty_cell(index)
                    self._current_dragged_item = item
                    self._dragged_item_index = index
                    self._dragged_item_inventory = inventory
                    self.display_item_dragged_pos()
                    self._last_time_clicked = monotonic()
                    return True
            else:
                removed_qty = inventory.add_element_at_pos(*self._current_dragged_item, index)
                self._current_dragged_item = (self._current_dragged_item[0], self._current_dragged_item[1] - removed_qty)
                if removed_qty == 0:
                    dragged_item = self._current_dragged_item
                    self._current_dragged_item = (items.NOTHING, 0)
                    self._last_time_clicked = 0
                    self._dragged_item_element = self._dragged_item_element.delete()
                    self.drag_item_in_inventory(inventory, index)
                    inventory.add_element_at_pos(*dragged_item, index)

                if self._current_dragged_item[1] == 0:
                    self._current_dragged_item = (items.NOTHING, 0)
                    self._dragged_item_index = -1
                    self._dragged_item_inventory = None
                    self._dragged_item_element = self._dragged_item_element.delete()
                    self._last_time_clicked = monotonic()
                return True
        return False

    def place_back_dragged_item(self) -> None:
        if self._dragged_item_index == -1: return
        item, qty = self._current_dragged_item
        qty -= self._dragged_item_inventory.add_element_at_pos(item, qty, self._dragged_item_index)
        if qty > 0:
            qty -= self._dragged_item_inventory.add_element(item, qty)
        if qty == 0:
            item = items.NOTHING
            self._dragged_item_index = -1
            self._dragged_item_inventory = None
            self._dragged_item_element = self._dragged_item_element.delete()
        self._current_dragged_item = (item, qty)

    def drag_item_in_inventories(self) -> bool:
        return self.drag_item_in_inventory(self.hot_bar_inventory) \
            or self.drag_item_in_inventory(self.main_inventory)

    def place_block(self, pos: tuple[int, int]) -> dict|None:
        if self.drag_item_in_inventories(): return {}
        if self.main_inventory.is_opened(): return
        x, y = self._get_relative_pos(*pos)
        # place block under player
        if self.left_player_pos <= x <= self.right_player_pos and self.bottom_player_pos <= y < self.top_player_pos:
            is_valid_pos = True
            for x in range(-(self.entity_size[0] // 2), self.entity_size[0] // 2 + 1):
                block = self.chunk_manager.get_block(self.x, self.y + self.top_player_pos)
                if block == blocks.NOTHING or block not in blocks.TRAVERSABLE_BLOCKS:
                    is_valid_pos = False
                    break
            if is_valid_pos and self._is_surrounded_by_block(self.x, self.y):
                self.y += 1
                y = -1
            else:
                return None
        else:
            if not self._is_interactable(x, y): return None
        block_x, block_y = self.x + x, self.y + y
        block = self.chunk_manager.get_block(block_x, block_y)
        if block in blocks.TRAVERSABLE_BLOCKS and self._is_surrounded_by_block(block_x, block_y):
            item, _ = self.hot_bar_inventory.remove_element_at_pos(1, self.hot_bar_inventory.get_selected_index())
            if item is None: return None
            block = convert_item_to_block(item)
            if block is not None:
                self.chunk_manager.replace_block(block_x, block_y, block)
                return {'changed_block': (block_x, block_y, block)}
            else:
                self.hot_bar_inventory.add_element_at_pos(item, 1, self.hot_bar_inventory.get_selected_index())

    def remove_block(self, pos: tuple[int, int]) -> dict|None:
        if self.main_inventory.is_opened(): return
        x, y = self._get_relative_pos(*pos)
        if not self._is_interactable(x, y): return None
        block_x, block_y = self.x + x, self.y + y
        block = self.chunk_manager.get_block(block_x, block_y)
        if block is not None and block not in blocks.TRAVERSABLE_BLOCKS:
            self.chunk_manager.replace_block(block_x, block_y, blocks.AIR)
            for item, quantity in convert_block_to_items(block, 1).items():
                quantity -= self.hot_bar_inventory.add_element(item, quantity)
                if quantity:
                    self.main_inventory.add_element(item, quantity)
            return {'changed_block': (block_x, block_y, blocks.AIR)}

    def interact_with_block(self, pos: tuple[int, int]):# -> tuple[type[BlockMenu]|None, tuple[int, int]|None]:
        if self.main_inventory.is_opened(): return None, None
        x, y = self._get_relative_pos(*pos)
        if not self._is_interactable(x, y): return None, None
        x, y = self.x + x, self.y + y
        block = self.chunk_manager.get_block(x, y)
        menu = blocks.INTERACTABLE_BLOCKS.get(block, None)
        if menu is not None:
            return menu, (x, y)
        return None, None

    def get_all_infos(self) -> dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'images-name': self.images_name
        }

    def get_infos(self) -> dict[str, Any]:
        return {
            'x': self.x,
            'y': self.y,
            'direction': self.direction
        }