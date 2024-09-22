from pygame import image as pgimg, transform, Surface
import os
from module_infos import SRC_PATH, RESOURCES_PATH

UNKNOWN_IMAGE_PATH = os.path.join(RESOURCES_PATH, 'images/unknown.png')

def load_image(paths: list[str], size: tuple[int, int]|None) -> Surface:
    image = None
    for path in paths:
        try:
            if not os.path.isabs(path):
                path = f'{SRC_PATH}/{path}'
            image = pgimg.load(path)
            break
        except FileNotFoundError:
            pass
    if image is None:
        image = pgimg.load(UNKNOWN_IMAGE_PATH)
    if size is None:
        return image.convert_alpha()
    return transform.scale(image.convert_alpha(), size)