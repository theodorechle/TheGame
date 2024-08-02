import pygame
import blocks
from conversions_items_blocks import convert_block_to_items, convert_item_to_block
from map_generation import MapGenerator
from save_manager_interface import SaveManagerInterface
from entity import Entity
from inventory import Inventory
from player_interface import PlayerInterface
from items import Item
from blocks_menus.block_menu import BlockMenu

class Player(Entity, PlayerInterface):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, window: pygame.Surface, map_generator: MapGenerator, save_manager: SaveManagerInterface, inventory_cells: list[tuple[Item|None, int]]|None=None) -> None:
        self.render_distance: int = 1
        self.interaction_range: int = 1 # doesn't work
        self.save_manager: SaveManagerInterface = save_manager

        self.infos_font_name: str = ""
        self.infos_font_size: int = 20
        self.infos_font: pygame.font.Font = pygame.font.SysFont(self.infos_font_name, self.infos_font_size)

        super().__init__(name, x, y, speed_x, speed_y, direction, window, 1, 2, map_generator, save_manager, 'persos', True)
        self.inventory_size: int = 50
        self.inventory: Inventory = Inventory(self.inventory_size, window, inventory_cells)
        self.set_player_edges_pos()

    
    def display_hud(self) -> None:
        self.inventory.display()
        self._display_infos()

    def _display_infos(self) -> None:
        infos: list[str] = []
        infos.append(f'coords: x: {self.x}, y: {self.y}')
        chunk = self.chunk_manager.get_chunk_and_coordinates(self.x, self.y)[0]
        infos.append(f'chunk: {chunk.id if chunk is not None else ""}')
        infos.append(f'biome: {chunk.biome.name if chunk is not None else ""}')
        infos.append(f'forest: {chunk.is_forest if chunk is not None else ""}')

        for i, info in enumerate(infos, start=1):
            self.window.blit(self.infos_font
                    .render(info, True, "#000000"), (50, 20 * i))

    def update(self, delta_t: float) -> bool:
        need_update = super().update(delta_t) or self.inventory.have_clicked_item()
        self.chunk_manager.update(self.x)
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

    def place_block(self, pos: tuple[int, int]) -> dict|None:
        if self.inventory.click_cell(*pos): return {} # temp
        if self.inventory.is_inventory_opened(): return
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
            item, _ = self.inventory.remove_element_at_pos(1, self.inventory.selected)
            if item is None: return None
            block = convert_item_to_block(item)
            if block is not None:
                self.chunk_manager.replace_block(block_x, block_y, block)
                return {'changed_block': (block_x, block_y, block)}
            else:
                self.inventory.add_element_at_pos(item, 1, self.inventory.selected)

    def remove_block(self, pos: tuple[int, int]) -> dict|None:
        if self.inventory.is_inventory_opened(): return
        x, y = self._get_relative_pos(*pos)
        if not self._is_interactable(x, y): return None
        block_x, block_y = self.x + x, self.y + y
        block = self.chunk_manager.get_block(block_x, block_y)
        if block is not None and block not in blocks.TRAVERSABLE_BLOCKS:
            self.chunk_manager.replace_block(block_x, block_y, blocks.AIR)
            for item, quantity in convert_block_to_items(block, 1).items():
                self.inventory.add_element(item, quantity)
            return {'changed_block': (block_x, block_y, blocks.AIR)}

    def interact_with_block(self, pos: tuple[int, int]) -> BlockMenu|None:
        if self.inventory.is_inventory_opened(): return
        x, y = self._get_relative_pos(*pos)
        if not self._is_interactable(x, y): return None
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        return blocks.INTERACTABLE_BLOCKS.get(block, None)


    def display(self) -> None:
        super().display(self.x, self.y)