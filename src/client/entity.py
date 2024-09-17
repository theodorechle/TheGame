from load_image import load_image
import pygame
import blocks
from chunk_manager import ChunkManager
from entity_interface import EntityInterface
from map_chunk import Chunk
from module_infos import RESOURCES_PATH
from typing import Any

ENTITIES_IMAGES_PATH: str = f'{RESOURCES_PATH}/images'

class Entity(EntityInterface):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, image_length: int, image_height: int, collisions: bool=True) -> None:
        """
        Base class for entities.
        They can move, and have collisions or not.
        If no chunk manager is given, collisions are disabled, because we can't check if they collide with blocks.
        """
        self.collisions = collisions
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.speed_x: int = speed_x
        self.speed_y: int = speed_y
        self.direction: bool = direction # False if right, True if left
        # number of blocks width and height
        self.entity_size: tuple[int, int] = (image_length, image_height)

    def set_player_edges_pos(self) -> None:
        self.top_player_pos: int = self.entity_size[1]
        self.bottom_player_pos: int = 0
        self.left_player_pos: int = -self.entity_size[0] // 2 + self.entity_size[0] % 2
        self.right_player_pos: int = self.entity_size[0] // 2

    def update(self, update_dict: dict[str, Any]) -> None:
        for key, value in update_dict.items():
            if key == 'x':
                self.x = value
            elif key == 'y':
                self.y = value

class DrawableEntity(Entity):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, image_length: int, image_height: int, window: pygame.Surface, add_path: str = '', collisions: bool = True, images_name: str="") -> None:
        self.window = window
        super().__init__(name, x, y, speed_x, speed_y, direction, image_length, image_height, collisions)
        self.path = ENTITIES_IMAGES_PATH
        if add_path:
            self.path += '/' + add_path
        self.images_name = images_name
        self.scale_image()

    def scale_image(self) -> None:
        self.image_size = (self.entity_size[0] * blocks.Block.BLOCK_SIZE, self.entity_size[1] * blocks.Block.BLOCK_SIZE)
        self.image: pygame.Surface = load_image([f'{self.path}/{self.images_name}.png'], self.image_size)
        self.image_reversed: pygame.Surface = load_image([f'{self.path}/{self.images_name}_reversed.png'], self.image_size)

    def display(self, rel_x: int, rel_y: int) -> None:
        """
        rel_x and rel_y are the coords of the block in the center of the image
        """
        window_size = self.window.get_size()
        x = window_size[0] // 2 - self.entity_size[0] * blocks.Block.BLOCK_SIZE // 2 + (self.x - rel_x) * blocks.Block.BLOCK_SIZE
        y = window_size[1] // 2 - self.image_size[1] + (rel_y - self.y) * blocks.Block.BLOCK_SIZE
        self.window.blit(
            self.image_reversed if self.direction else self.image,
            (x, y)
        )