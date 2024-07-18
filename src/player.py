from load_image import load_image
import chunk_manager
from pygame import Surface
import blocks
import items
from recipes import convert_block_to_items, convert_item_to_block

class Inventory:
    def __init__(self, nb_cells: int) -> None:
        self.nb_cells = nb_cells
        self.cells: list[list[int, int]] = [[items.NOTHING, 0] for _ in range(self.nb_cells)] # list of list with items and quantities
    
    def add_element_at_pos(self, element: items.Item, quantity: int, pos: int) -> int:
        """
        Tries to add the quantity of the given element in the inventory at pos.
        Returns the quantity effectively added.
        """
        if 0 > pos or pos >= len(self.cells): return 0
        if self.cells[pos][0] == items.NOTHING: self.cells[pos][0] = element
        elif self.cells[pos][0] != element: return 0
        added_quantity = min(quantity, element.stack_size - self.cells[pos][1])
        self.cells[pos][1] += added_quantity
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
    
    def remove_element_at_pos(self, quantity: int, pos: int) -> tuple[items.Item, int]:
        """
        Tries to remove the quantity of the element in the inventory at pos.
        Returns the quantity effectively removed.
        """
        if 0 > pos or pos >= len(self.cells): return 0
        removed_quantity = min(quantity, self.cells[pos][1])
        cell = [self.cells[pos][0], removed_quantity]
        self.cells[pos][1] -= removed_quantity
        if self.cells[pos][1] == 0:
            self.cells[pos] = [items.NOTHING, 0]
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
                self.cells[index] = [items.NOTHING, 0]
        return removed_quantity

    def empty_cell(self, pos: int) -> tuple[items.Item, int]:
        """
        Empty the inventory's cell at pos.
        Returns a tuple containing the item in the cell and the quantity of it.
        """
        if 0 > pos or pos >= len(self.cells): return [items.NOTHING, 0]
        cell = self.cells[pos]
        self.cells[pos] = [items.NOTHING, 0]
        return cell

    def sort(self) -> None:
        ...

class Player:
    PLAYER_SIZE = (1, 2) # number of blocks width and height
    image_size = (PLAYER_SIZE[0] * blocks.Block.BLOCK_SIZE, PLAYER_SIZE[1] * blocks.Block.BLOCK_SIZE)
    PATH = 'src/resources/images/persos'
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, window: Surface) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.window = window
        self.render_distance = 3
        self.interaction_range = 1
        self.chunk_manager = chunk_manager.ChunkManager(3, 0, window)
        self.chunk_manager.chunks[3].chunk[15][8] = blocks.GRASS
        self.chunk_manager.chunks[0].chunk[16][0] = blocks.COAL
        self.chunk_manager.chunks[0].chunk[15][1] = blocks.IRON
        self.image = None
        self.image_reversed = None
        self.direction = False # False if right, True if left
        self.inventory_size = 10
        self.inventory = Inventory(self.inventory_size)
    
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

    def update(self) -> None:
        is_valid_pos = True
        for x in range(-(self.PLAYER_SIZE[0] // 2), self.PLAYER_SIZE[0] // 2 + 1):
            block = self.chunk_manager.get_block(self.x + x, self.y - 1)
            if block == -1 or block != blocks.AIR:
                is_valid_pos = False
                break
        if is_valid_pos:
            self.y -= 1
        if not self.speed_x: return
        sign = (1 if self.speed_x >= 0 else -1)
        new_direction = (sign == -1)
        if new_direction != self.direction:
            self.direction = new_direction
        else:
            for _ in range(abs(self.speed_x)):
                is_valid_pos = True
                for y in range(1, self.PLAYER_SIZE[1]):
                    if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y + y) != blocks.AIR:
                        is_valid_pos = False
                        break
                if is_valid_pos:
                    if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y) != blocks.AIR:
                        if self.chunk_manager.get_block(self.x + (self.PLAYER_SIZE[0] // 2 + 1) * sign, self.y + self.PLAYER_SIZE[1])  == blocks.AIR:
                            self.y += 1
                        else:
                            continue
                    self.x += sign
        self.speed_x = sign * (abs(self.speed_x) // 2)

    def save(self) -> None:
        ...
    
    def _get_relative_pos(self, x: int, y: int) -> tuple[int, int]:
        x = (x - self.window.get_size()[0] // 2 + blocks.Block.BLOCK_SIZE // 2) // blocks.Block.BLOCK_SIZE
        y = -(y - self.window.get_size()[1] // 2) // blocks.Block.BLOCK_SIZE
        return x, y
    
    def _is_interactable(self, x: int, y: int) -> bool:
        rx, ry = self._get_relative_pos(x, y)
        if 0 <= ry < self.PLAYER_SIZE[1]: # left or right
            if self.direction:
                return rx == -self.PLAYER_SIZE[0] // 2 - (not self.PLAYER_SIZE[0] % 2)
            else:
                return rx == self.PLAYER_SIZE[0] // 2 + 1
        elif ry == -1 or ry == self.PLAYER_SIZE[1]: # down or up
            if -self.PLAYER_SIZE[0] // 2 + self.PLAYER_SIZE[0] % 2 <= rx <= self.PLAYER_SIZE[0] // 2:
                return True
            elif -self.PLAYER_SIZE[0] // 2 + self.PLAYER_SIZE[0] % 2 - 1 == rx:
                if ry == -1:
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry + 1) == blocks.AIR or self.chunk_manager.get_block(self.x + rx + 1, self.y + ry) == blocks.AIR
                else:
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry - 1) == blocks.AIR or self.chunk_manager.get_block(self.x + rx + 1, self.y + ry) == blocks.AIR
            elif rx == self.PLAYER_SIZE[0] // 2 + 1:
                if ry == -1:
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry + 1) == blocks.AIR or self.chunk_manager.get_block(self.x + rx - 1, self.y + ry) == blocks.AIR
                else:
                    return self.chunk_manager.get_block(self.x + rx, self.y + ry - 1) == blocks.AIR or self.chunk_manager.get_block(self.x + rx - 1, self.y + ry) == blocks.AIR
        else:
            return False

    def place_block(self, pos: tuple[int, int]) -> None:
        if not self._is_interactable(*pos): return
        x, y = self._get_relative_pos(*pos)
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        if block == blocks.AIR:
            item, quantity = self.inventory.remove_element_at_pos(1, 0)
            if quantity == 0: return
            block = convert_item_to_block(item)
            if block != None:
                self.chunk_manager.replace_block(self.x + x, self.y + y, block)

    def remove_block(self, pos: tuple[int, int]) -> None:
        if not self._is_interactable(*pos): return
        x, y = self._get_relative_pos(*pos)
        block = self.chunk_manager.get_block(self.x + x, self.y + y)
        if block != blocks.AIR:
            self.chunk_manager.replace_block(self.x + x, self.y + y, blocks.AIR)
            for item, quantity in convert_block_to_items(block, 1).items():
                self.inventory.add_element(item, quantity)