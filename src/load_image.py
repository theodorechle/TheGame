from pygame import image as pgimg, transform, Surface

UNKNOWN_IMAGE_PATH = 'src/resources/images/unknown.png'

def load_image(path: str, size: tuple[int, int]) -> Surface:
    try:
        image = pgimg.load(path)
    except FileNotFoundError:
        image = pgimg.load(UNKNOWN_IMAGE_PATH)
    return transform.scale(image.convert_alpha(), size)