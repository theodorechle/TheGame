from pygame import image as pgimg, transform, Surface

UNKNOWN_IMAGE_PATH = 'src/resources/images/unknown.png'

def load_image(paths: list[str], size: tuple[int, int]) -> Surface:
    image = None
    for path in paths:
        try:
            image = pgimg.load(path)
            break
        except FileNotFoundError:
            pass
    if image is None:
        image = pgimg.load(UNKNOWN_IMAGE_PATH)

    return transform.scale(image.convert_alpha(), size)