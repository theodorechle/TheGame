import blocks
from entities.entity import Entity
from inventory import Inventory
from entities.player_interface import PlayerInterface
import items
from time import monotonic
from chunk_manager import ChunkManager
from typing import Any
from conversions_items_blocks import convert_block_to_items, convert_item_to_block

class Player(Entity, PlayerInterface):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, chunk_manager: ChunkManager, main_inventory_cells: list[tuple[items.Item|None, int]]|None=None, hot_bar_inventory_cells: list[tuple[items.Item|None, int]]|None=None, images_name: str="") -> None:
        PlayerInterface.__init__(self)
        self.interaction_range: int = 1 # doesn't work

        Entity.__init__(self, name, x, y, speed_x, speed_y, direction, 1, 2, chunk_manager, 'persos', True, images_name=images_name)
        self.inventory_size: int = 50
        self.main_inventory: Inventory = Inventory(self.inventory_size - 10, main_inventory_cells, classes_names=['main-inventory'], anchor='center')
        self.hot_bar_inventory: Inventory = Inventory(10, hot_bar_inventory_cells, classes_names=['hot-bar-inventory'], anchor='bottom')
        self.set_player_edges_pos()

    def update(self, delta_t: float) -> bool:
        self.item_clicked_last_frame = False
        need_update = super().update(delta_t) or self.force_update
        self.force_update = False
        return need_update

    def save(self) -> None:
        self.chunk_manager.save_chunks()
    
    def _get_relative_pos(self, x: int, y: int) -> tuple[int, int]:
        x = (x - self.window.get_size()[0] // 2 + blocks.block_size // 2) // blocks.block_size
        y = -(y - self.window.get_size()[1] // 2) // blocks.block_size
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

    def place_block(self, pos: tuple[int, int], selected_item_index: int) -> tuple[blocks.Block, tuple[int, int]]|None:
        block_x, block_y = pos

        # place block under player
        place_block_under = False
        if self.x + self.left_player_pos <= block_x <= self.x + self.right_player_pos \
                and self.y + self.bottom_player_pos <= block_y < self.y + self.top_player_pos:
            place_block_under = True
            for x in range(-(self.entity_size[0] // 2), self.entity_size[0] // 2 + 1):
                block = self.chunk_manager.get_block(self.x + x, self.y + self.top_player_pos)
                if block == blocks.NOTHING or block not in blocks.TRAVERSABLE_BLOCKS:
                    return
            block_y = self.y
        elif not self._is_interactable(block_x - self.x, block_y - self.y): return
        
        if not self._is_surrounded_by_block(block_x, block_y): return
        block = self.chunk_manager.get_block(block_x, block_y)
        if block in blocks.TRAVERSABLE_BLOCKS:
            item, _ = self.hot_bar_inventory.remove_element_at_pos(1, selected_item_index)
            if item is None: return
            new_block = convert_item_to_block(item)
            if new_block != blocks.NOTHING:
                self.chunk_manager.replace_block(block_x, block_y, new_block)
                self.force_update = True
                if place_block_under:
                    self.y += 1
                return (new_block, (block_x, block_y))
            self.hot_bar_inventory.add_element_at_pos(item, 1, selected_item_index)

    def remove_block(self, pos: tuple[int, int]) -> tuple[blocks.Block, tuple[int]]|None:
        block_x, block_y = pos
        if not self._is_interactable(block_x - self.x, block_y - self.y): return None
        block = self.chunk_manager.get_block(block_x, block_y)
        if block != blocks.NOTHING and block not in blocks.TRAVERSABLE_BLOCKS:
            self.chunk_manager.replace_block(block_x, block_y, blocks.AIR)
            for item, quantity in convert_block_to_items(block, 1).items():
                quantity -= self.hot_bar_inventory.add_element(item, quantity)
                if quantity:
                    self.main_inventory.add_element(item, quantity)
            self.force_update = True
            return (blocks.AIR, (block_x, block_y))

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
            'images-name': self.images_name,
            'main_inventory': self.main_inventory.cells,
            'hot_bar_inventory': self.hot_bar_inventory.cells
        }

    def get_infos(self) -> dict[str, Any]:
        infos = {
            'x': self.x,
            'y': self.y,
            'direction': self.direction
        }
        update_main_inventory = self.main_inventory.get_updated_items()
        if update_main_inventory:
            infos['main_inventory_updated'] = update_main_inventory
        update_hot_bar_inventory = self.hot_bar_inventory.get_updated_items()
        if update_hot_bar_inventory:
            infos['hot_bar_inventory_updated'] = update_hot_bar_inventory
        return infos