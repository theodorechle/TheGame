import blocks

class Biome:
    PATH = 'resources/biomes'
    def __init__(self, name: str,
                 min_height: int,
                 max_height: int,
                 max_height_difference: int,
                 is_water_biome: bool,
                 upper_block: blocks.Block,
                 blocks_by_zone: list[tuple[blocks.Block, int]]) -> None:
        self.name = name
        self.min_height = min_height
        self.max_height = max_height
        self.max_height_difference = max_height_difference
        self.is_water_biome = is_water_biome
        self.upper_block = upper_block
        # (block, min_height)
        self.blocks_by_zone = blocks_by_zone

def get_biome_environment_values(biome: Biome) -> tuple[int, int, int, int]|None:
    for vars, biome_ in BIOMES.items():
        if biome_ == biome:
            return vars
    return None

PLAIN = Biome('plain', 50, 60, 1, False, blocks.GRASS, [(blocks.EARTH, 40)])
HILL = Biome('hill', 60, 80, 2, False, blocks.GRASS, [(blocks.EARTH, 50)])
MOUNTAIN = Biome('mountain', 100, 115, 3, False, blocks.STONE, [])
LAKE = Biome('lake', 30, 40, 1, True, blocks.SAND, [(blocks.SAND, 32)])

# tuple (is_island, height, temperature, humidity)
BIOMES = {
    (1, 0, 0, 0): PLAIN,
    (1, 1, 0, 0): HILL,
    (1, 2, 0, 0): MOUNTAIN,
    (0, 0, 0, 0): LAKE
}