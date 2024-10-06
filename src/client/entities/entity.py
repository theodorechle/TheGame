from load_image import load_image
import pygame
import blocks
from entities.entity_interface import EntityInterface
from module_infos import RESOURCES_PATH
from typing import Any
from gui.ui_manager import UIManager
from gui.elements import Label

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
            elif key == 'direction':
                self.direction = value

class DrawableEntity(Entity):
    def __init__(self, name: str, x: int, y: int, speed_x: int, speed_y: int, direction: bool, image_length: int, image_height: int, ui_manager: UIManager=None, add_path: str = '', collisions: bool = True, images_name: str="", display_name: bool=False) -> None:
        self._ui_manager = ui_manager
        self.display_name = display_name
        super().__init__(name, x, y, speed_x, speed_y, direction, image_length, image_height, collisions)
        self.name_label = None if not self.display_name else Label(self._ui_manager, self.name, anchor='center', classes_names=['player-name'])
        self.path = ENTITIES_IMAGES_PATH
        if add_path:
            self.path += '/' + add_path
        self.images_name = images_name
        self.load_image()

    def load_image(self) -> None:
        self.image_size = (self.entity_size[0] * blocks.block_size, self.entity_size[1] * blocks.block_size)
        self.image: pygame.Surface = load_image([f'{self.path}/{self.images_name}.png'], self.image_size)
        self.image_reversed: pygame.Surface = load_image([f'{self.path}/{self.images_name}_reversed.png'], self.image_size)

    def display(self, rel_x: int, rel_y: int) -> None:
        """
        rel_x and rel_y are the coords of the block in the center of the image
        """
        window_size = self._ui_manager.get_window_size()
        center_x = window_size[0] // 2 + (self.x - rel_x) * blocks.block_size
        x = center_x - self.entity_size[0] * blocks.block_size // 2
        y = window_size[1] // 2 - self.image_size[1] + (rel_y - self.y) * blocks.block_size
        self._ui_manager.get_window().blit(
            self.image_reversed if self.direction else self.image,
            (x, y)
        )
        if self.name_label is not None:
            self.name_label._first_coords = ((self.x - rel_x) * blocks.block_size, -self.image_size[1] + (rel_y - self.y) * blocks.block_size - 10)
            self.name_label.update_element()
            self._ui_manager.ask_refresh(self.name_label)
    
    def delete(self) -> None:
        if self.name_label is not None:
            self._ui_manager.remove_element(self.name_label)
    