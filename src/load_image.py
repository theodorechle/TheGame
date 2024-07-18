from pygame import image as pgimg, transform, Surface

UNKNOWN_IMAGE_PATH = 'src/resources/images/unknown.png'

def load_image(paths: list[str], size: tuple[int, int]) -> Surface:
    is_loaded = False
    for path in paths:
        try:
            image = pgimg.load(path)
            is_loaded = True
            break
        except FileNotFoundError:
            ...
    if not is_loaded:
        image = pgimg.load(UNKNOWN_IMAGE_PATH)
    return transform.scale(image.convert_alpha(), size)