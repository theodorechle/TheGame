from pygame import image as pgimg, transform, Surface
import os
from client.module_infos import MODULE_PATH

UNKNOWN_IMAGE_PATH = 'src/resources/images/unknown.png'

def load_image(paths: list[str], size: tuple[int, int]|None) -> Surface:
    image = None
    for path in paths:
        try:
            if not os.path.isabs(path):
                path = f'{MODULE_PATH}/{path}'
            image = pgimg.load(path)
            break
        except FileNotFoundError:
            pass
    if image is None:
        image = pgimg.load(UNKNOWN_IMAGE_PATH)
    if size is None:
        return image.convert_alpha()
    return transform.scale(image.convert_alpha(), size)