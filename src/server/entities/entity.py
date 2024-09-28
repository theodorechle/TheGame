import blocks
from chunk_manager import ChunkManager
from entities.entity_interface import EntityInterface

ENTITIES_IMAGES_PATH: str = 'src/resources/images'
class Entity(EntityInterface):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, image_length: int, image_height: int, chunk_manager: ChunkManager, add_path: str='', collisions: bool=True, images_name: str="") -> None:
        """
        Base class for entities.
        They can move, and have collisions or not.
        If no chunk manager is given, collisions are disabled, because we can't check if they collide with blocks.
        """
        self.chunk_manager: ChunkManager = chunk_manager
        self.collisions = collisions
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.speed_x: int = speed_x
        self.speed_y: int = speed_y
        self.direction: bool = direction # False if right, True if left
        # number of blocks width and height
        self.entity_size: tuple[int, int] = (image_length, image_height)
        self.images_name = images_name
        self.force_update = False

    def set_player_edges_pos(self) -> None:
        self.top_player_pos: int = self.entity_size[1]
        self.bottom_player_pos: int = 0
        self.left_player_pos: int = -self.entity_size[0] // 2 + self.entity_size[0] % 2
        self.right_player_pos: int = self.entity_size[0] // 2

    def update(self, delta_t: float) -> bool:
        """
        Move the player if needed
        Return whether the player has moved or not
        """
        need_update = False
        can_fall: bool = True
        if self.speed_y > 0: # Go up
            in_water = False
            if self.collisions:
                for x in range(-(self.entity_size[0] // 2), self.entity_size[0] // 2 + 1):
                    for y in range(self.entity_size[1]):
                        block = self.chunk_manager.get_block(self.x + x, self.y + y)
                        if block is not blocks.NOTHING and block in blocks.SWIMMABLE_BLOCKS:
                            in_water = True
                            break
            if not self.collisions or in_water:
                is_valid_pos = True
                if self.collisions:
                    for x in range(-(self.entity_size[0] // 2), self.entity_size[0] // 2 + 1):
                        block = self.chunk_manager.get_block(self.x + x, self.y + self.top_player_pos)
                        if block is not blocks.NOTHING and block not in blocks.TRAVERSABLE_BLOCKS:
                            is_valid_pos = False
                            break
                        block = self.chunk_manager.get_block(self.x + x, self.y + 1)
                        if block is not blocks.NOTHING and block not in blocks.SWIMMABLE_BLOCKS:
                            is_valid_pos = False
                            break
                if is_valid_pos:
                    self.y += 1
                    need_update = True
                if self.speed_y >= 1:
                    can_fall = False
                self.speed_y = 0
            else:
                self.speed_y = 0
        if self.speed_y <= 0 and can_fall: # Fall
            is_valid_pos = True
            if self.collisions:
                for x in range(-(self.entity_size[0] // 2), self.entity_size[0] // 2 + 1):
                    block = self.chunk_manager.get_block(self.x + x, self.y - 1)
                    if block is not blocks.NOTHING and block not in blocks.TRAVERSABLE_BLOCKS:
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
                if self.collisions:
                    for y in range(1, self.entity_size[1]):
                        if self.chunk_manager.get_block(self.x + (self.entity_size[0] // 2 + 1) * sign, self.y + y) not in blocks.TRAVERSABLE_BLOCKS:
                            is_valid_pos = False
                            break
                if is_valid_pos:
                    if self.collisions:
                        # check if need to jump up to the next block
                        if self.chunk_manager.get_block(self.x + (self.entity_size[0] // 2 + 1) * sign, self.y) not in blocks.TRAVERSABLE_BLOCKS:
                            if self.chunk_manager.get_block(self.x + (self.entity_size[0] // 2 + 1) * sign, self.y + self.entity_size[1]) in blocks.TRAVERSABLE_BLOCKS \
                                    and self.chunk_manager.get_block(self.x + (self.entity_size[0] // 2) * sign, self.y + self.entity_size[1]) in blocks.TRAVERSABLE_BLOCKS:
                                self.y += 1
                            else:
                                continue
                    self.x += sign
                    need_update = True
        self.speed_x = sign * (abs(self.speed_x) // 2)
        return need_update
