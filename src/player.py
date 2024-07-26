from load_image import load_image
import chunk_manager
import pygame
import blocks
import items
from recipes import convert_block_to_items, convert_item_to_block
from map_generation import MapGenerator
from time import monotonic

class Inventory:
    def __init__(self, nb_cells: int, window: pygame.Surface) -> None:
        self._nb_cells = nb_cells
        self._cells: list[list[items.Item, int]] = [[items.NOTHING, 0] for _ in range(self._nb_cells)] # list of list with items and quantities
        self.window = window
        self.cell_size = 40
        self.nb_cells_by_line = 10
        self.cells_borders_size = 2
        self.blocks_qty_font_name = ""
        self.blocks_qty_font_size = 20
        self.block_qty_font = pygame.font.SysFont(self.blocks_qty_font_name, self.blocks_qty_font_size)
        self.selected = 0
        self._display_all = False
        self.main_bar_start_pos = (0, self.window.get_size()[1] - self.cell_size)
        self.complete_inventory_start_pos = (0, self.window.get_size()[1] // 2)
        # item, quantity
        self._current_clicked_item: tuple[items.Item, int] = (items.NOTHING, 0)
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
        if self._cells[pos][0] == items.NOTHING: self._cells[pos][0] = element
        elif self._cells[pos][0] != element: return 0
        added_quantity = min(quantity, element.stack_size - self._cells[pos][1])
        self._cells[pos][1] += added_quantity
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
    
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
        if 0 > pos or pos >= len(self._cells): return 0
        removed_quantity = min(quantity, self._cells[pos][1])
        cell = [self._cells[pos][0], removed_quantity]
        self._cells[pos][1] -= removed_quantity
        if self._cells[pos][1] == 0:
            self._cells[pos] = [items.NOTHING, 0]
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
                self._cells[index] = [items.NOTHING, 0]
        return removed_quantity

    def empty_cell(self, pos: int) -> tuple[items.Item, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
        if 0 > pos or pos >= len(self._cells): return [items.NOTHING, 0]
        cell = self._cells[pos]
        self._cells[pos] = [items.NOTHING, 0]
        return cell

    def sort(self) -> None:
        ...

    def display(self) -> None:
        self.display_main_bar()
        if self._display_all:
            for index in range(10, len(self._cells)):
                x, y = self.complete_inventory_start_pos[0] + (index % self.nb_cells_by_line) * self.cell_size, self.complete_inventory_start_pos[1] + (index // self.nb_cells_by_line) * self.cell_size
                self._display_cell(x, y, False)
                block, qty = self._cells[index]
                if block is None: continue
                self._display_block(x, y, block, qty)
        if self._clicked_item_init_pos != -1:
            self._display_block(*pygame.mouse.get_pos(), *self._current_clicked_item)
    
    def display_main_bar(self) -> None:
        for index in range(10):
            x, y = self.main_bar_start_pos[0] + index * self.cell_size, self.main_bar_start_pos[1]
            self._display_cell(x, y, self.selected == index)
            if index >= len(self._cells): continue
            block, qty = self._cells[index]
            if block is None: continue
            self._display_block(x, y, block, qty)

    def _display_cell(self, x: int, y: int, selected: bool) -> None:
        border_size = self.cells_borders_size * (1 + selected)
        pygame.draw.rect(self.window, "#dddddd", pygame.Rect(x, y, self.cell_size, self.cell_size))
        pygame.draw.rect(self.window, "#aaaaaa", pygame.Rect(x, y, self.cell_size, self.cell_size), border_size)

    def _display_block(self, x: int, y: int, block: blocks.Block, qty: int) -> None:
        item_img_start = (self.cell_size - items.Item.ITEM_SIZE) // 2
        self.window.blit(block.image, (x + item_img_start, y + item_img_start))
        qty = str(qty)
        qty_render_size = self.block_qty_font.size(qty)
        self.window.blit(self.block_qty_font
                            .render(qty, True, "#000000"), (x + self.cell_size - qty_render_size[0], y + self.cell_size - qty_render_size[1]))

    def toggle_inventory(self) -> bool:
        """
        Returns whether it needs a screen update or not
        """
        if self._last_time_toggled > monotonic() - self.time_before_toggle: return False
        self._display_all = not self._display_all 
        self._last_time_toggled = monotonic()
        return True

    def click_cell(self, x: int, y: int) -> bool:
        if self._last_time_clicked > monotonic() - self.time_before_click: return
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
                index = y * self.nb_cells_by_line + x
            else: return False
        else:
            return False
        if index >= self._nb_cells: return False
        if self._clicked_item_init_pos == -1:
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


class Player:
    PLAYER_SIZE = (1, 2) # number of blocks width and height
    image_size = (PLAYER_SIZE[0] * blocks.Block.BLOCK_SIZE, PLAYER_SIZE[1] * blocks.Block.BLOCK_SIZE)
    PATH = 'src/resources/images/persos'
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, window: pygame.Surface, map_generator: MapGenerator, clock: pygame.time.Clock) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.window = window
        self.render_distance = 25
        self.interaction_range = 1
        self.clock = clock

        self.infos_font_name = ""
        self.infos_font_size = 20
        self.infos_font = pygame.font.SysFont(self.infos_font_name, self.infos_font_size)

        self.chunk_manager = chunk_manager.ChunkManager(self.render_distance, 0, window, map_generator)
        self.image = None
        self.image_reversed = None
        self.direction = False # False if right, True if left
        self.inventory_size = 50
        self.inventory = Inventory(self.inventory_size, window)
        self.player_edges_pos()

    def player_edges_pos(self) -> None:
        self.top_player_pos = self.PLAYER_SIZE[1]
        self.bottom_player_pos = 0
        self.left_player_pos = -self.PLAYER_SIZE[0] // 2 + self.PLAYER_SIZE[0] % 2
        self.right_player_pos = self.PLAYER_SIZE[0] // 2
    
    def load_image(self) -> None:
        self.image = load_image([f'{self.PATH}/{self.name}.png'], self.image_size)
        self.image_reversed = load_image([f'{self.PATH}/{self.name}_reversed.png'], self.image_size)
    
    def display(self) -> None:
        window_size = self.window.get_size()
        self.window.blit(
            self.image_reversed if self.direction else self.image,
            (window_size[0] // 2 - self.PLAYER_SIZE[0] * blocks.Block.BLOCK_SIZE // 2,
             window_size[1] // 2 - self.image_size[1])
        )
    
    def display_hud(self) -> None:
        self.inventory.display()
        self._display_infos()

    def _display_infos(self):
        infos = []
        infos.append(f'coords: x: {self.x}, y: {self.y}')
        chunk = self.chunk_manager.get_chunk_and_coordinates(self.x, self.y)[0]
        infos.append(f'chunk: {chunk.id if chunk is not None else ""}')
        infos.append(f'biome: {chunk.biome if chunk is not None else ""}')
        infos.append(f'forest: {chunk.is_forest if chunk is not None else ""}')
        infos.append(f'FPS: {round(self.clock.get_fps())}')

        for i, info in enumerate(infos, start=1):
            self.window.blit(self.infos_font
                    .render(info, True, "#000000"), (50, 20 * i))

    def update(self) -> bool:
        """
        Return whether the player has moved or not
        """
        need_update = self.inventory._clicked_item_init_pos != -1
        if self.speed_y > 0: # Go up
            in_water = False
            for x in range(-(self.PLAYER_SIZE[0] // 2), self.PLAYER_SIZE[0] // 2 + 1):
                for y in range(self.PLAYER_SIZE[1]):
                    block = self.chunk_manager.get_block(self.x + x, self.y + y)
                    if block != -1 and block in blocks.SWIMMABLE_BLOCKS:
                        in_water = True
                        break
            if in_water:
                is_valid_pos = True
                for x in range(-(self.PLAYER_SIZE[0] // 2), self.PLAYER_SIZE[0] // 2 + 1):
                    block = self.chunk_manager.get_block(self.x + x, self.y + self.top_player_pos)
                    if block == -1 or block not in blocks.TRAVERSABLE_BLOCKS:
                        is_valid_pos = False
                        break
                    block = self.chunk_manager.get_block(self.x + x, self.y + 1)
                    if block == -1 or block not in blocks.SWIMMABLE_BLOCKS:
                        is_valid_pos = False
                        break
                if is_valid_pos:
                    self.y += 1
                    need_update = True
                if self.speed_y >= 1:
                    self.speed_y = 0.1
                else:
                    self.speed_y = 0
            else:
                self.speed_y = 0
        if self.speed_y <= 0: # Fall
            is_valid_pos = True
            for x in range(-(self.PLAYER_SIZE[0] // 2), self.PLAYER_SIZE[0] // 2 + 1):
                block = self.chunk_manager.get_block(self.x + x, self.y - 1)
                if block == -1 or block not in blocks.TRAVERSABLE_BLOCKS:
                    is_valid_pos = False
                    break
            if is_valid_pos:
                self.y -= 1
                need_update = True
        if not self.speed_x: return need_update
        sign = (1 if self.speed_x >= 0 else -1)
        new_direction = (sign == -1)
        if new_direction != self.direction:
            self.direction = new_direction
            need_update = True
        else:
            for _ in range(abs(self.speed_x)):
                is_valid_pos = True
                for y in range(1, self.PLAYER_SIZE[1]):
                    if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y + y) not in blocks.TRAVERSABLE_BLOCKS:
                        is_valid_pos = False
                        break
                if is_valid_pos:
                    if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y) not in blocks.TRAVERSABLE_BLOCKS:
                        if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y + self.PLAYER_SIZE[1]) in blocks.TRAVERSABLE_BLOCKS \
                                and self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2) * sign, self.y + self.PLAYER_SIZE[1]) in blocks.TRAVERSABLE_BLOCKS:
                            self.y += 1
                        else:
                            continue
                    self.x += sign
                    need_update = True
        self.speed_x = sign * (abs(self.speed_x) // 2)
        return need_update

    def save(self) -> None:
        ...
    
    def _get_relative_pos(self, x: int, y: int) -> tuple[int, int]:
        x = (x - self.window.get_size()[0] // 2 + blocks.Block.BLOCK_SIZE // 2) // blocks.Block.BLOCK_SIZE
        y = -(y - self.window.get_size()[1] // 2) // blocks.Block.BLOCK_SIZE
        return x, y
    
    def _is_interactable(self, x: int, y: int) -> bool:
        rx, ry = self._get_relative_pos(x, y)

        if self.bottom_player_pos-self.interaction_range + 1 <= ry < self.top_player_pos + self.interaction_range - 1: # left or right
            if self.direction:
                return rx == self.left_player_pos - self.interaction_range
            else:
                return rx == self.right_player_pos + self.interaction_range
        elif ry == self.bottom_player_pos-self.interaction_range or ry == self.top_player_pos + self.interaction_range - 1: # down or up
            if self.left_player_pos - self.interaction_range + 1 <= rx < self.right_player_pos + self.interaction_range:
                return True
            # edges
            elif self.left_player_pos - self.interaction_range == rx:
                if ry == self.bottom_player_pos-self.interaction_range: # down-left
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry + self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + rx + self.interaction_range, self.y + ry) in blocks.TRAVERSABLE_BLOCKS
                else: # up-left
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry - self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + rx + self.interaction_range, self.y + ry) in blocks.TRAVERSABLE_BLOCKS
            elif rx == self.PLAYER_SIZE[0] // 2 + self.interaction_range:
                if ry == self.bottom_player_pos-self.interaction_range: # down-right
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry + self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + rx - self.interaction_range, self.y + ry) in blocks.TRAVERSABLE_BLOCKS
                else: # up-right
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry - self.interaction_range) in blocks.TRAVERSABLE_BLOCKS or self.chunk_manager.get_block(self.x + rx - self.interaction_range, self.y + ry) in blocks.TRAVERSABLE_BLOCKS

    def _is_surrounded_by_block(self, x: int, y: int) -> bool:
        return (self.chunk_manager.get_block(x + 1, y) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x, y + 1) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x - 1, y) not in blocks.TRAVERSABLE_BLOCKS
                or self.chunk_manager.get_block(x, y - 1) not in blocks.TRAVERSABLE_BLOCKS)

    def place_block(self, pos: tuple[int, int]) -> bool:
        if self.inventory.click_cell(*pos): return True
        x, y = self._get_relative_pos(*pos)
        if self.left_player_pos <= x <= self.right_player_pos and self.bottom_player_pos <= y < self.top_player_pos:
            is_valid_pos = True
            for x in range(-(self.PLAYER_SIZE[0] // 2), self.PLAYER_SIZE[0] // 2 + 1):
                block = self.chunk_manager.get_block(self.x, self.y + self.top_player_pos)
                if block == -1 or block not in blocks.TRAVERSABLE_BLOCKS:
                    is_valid_pos = False
                    break
            if is_valid_pos and self._is_surrounded_by_block(self.x, self.y):
                self.y += 1
                y = -1
            else:
                return False
        else:
            if not self._is_interactable(*pos): return False
        block_x, block_y = self.x + x, self.y + y
        block = self.chunk_manager.get_block(block_x, block_y)
        if block in blocks.TRAVERSABLE_BLOCKS and self._is_surrounded_by_block(block_x, block_y):
            item, quantity = self.inventory.remove_element_at_pos(1, self.inventory.selected)
            if quantity == 0: return False
            block = convert_item_to_block(item)
            if block != None:
                self.chunk_manager.replace_block(block_x, block_y, block)
            else:
                self.inventory.add_element_at_pos(item, 1, self.inventory.selected)
        return True

    def remove_block(self, pos: tuple[int, int]) -> None:
        if not self._is_interactable(*pos): return False
        x, y = self._get_relative_pos(*pos)
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        if block not in blocks.TRAVERSABLE_BLOCKS:
            self.chunk_manager.replace_block(self.x + x, self.y + y, blocks.AIR)
            for item, quantity in convert_block_to_items(block, 1).items():
                self.inventory.add_element(item, quantity)
        return True