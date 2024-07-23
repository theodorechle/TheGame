import blocks

class Biome:
    PATH = 'resources/biomes'
    def __init__(self, name: str,
                 min_height: int,
                 max_height: int,
                 max_height_difference: int,
                 upper_block: blocks.Block,
                 blocks_by_zone: list[tuple[blocks.Block, int]],
                 ore_veins_qty: tuple[int, int],
                 ore_veins_repartition: list[tuple[float, blocks.Block, int, int, float]]) -> None:
        self.name = name
        self.min_height = min_height
        self.max_height = max_height
        self.max_height_difference = max_height_difference
        self.upper_block = upper_block
        # (block, min_height)
        self.blocks_by_zone = blocks_by_zone
        # (min_qty, max_qty)
        self.ore_veins_qty = ore_veins_qty
        # (probability, block, min_height, max_height, probability_to_expand)
        self.ore_veins_repartition = ore_veins_repartition

def get_biome_environment_values(biome: Biome) -> tuple[int, int, int, int]|None:
    for vars, biome_ in BIOMES.items():
        if biome_ == biome:
            return vars
    return None

PLAIN = Biome('plain', 50, 60, 1, blocks.GRASS,
              [(blocks.EARTH, 40)],
              (2, 10),
              [
    (0.6, blocks.COAL, 30, 40, 0.4),
    (0.4, blocks.IRON, 26, 37, 0.3)
])
HILL = Biome('hill', 60, 80, 2, blocks.GRASS,
             [(blocks.EARTH, 50)],
             (4, 10),
             [
    (0.6, blocks.COAL, 50, 60, 0.4),
    (0.4, blocks.IRON, 45, 57, 0.3)
])
MOUNTAIN = Biome('mountain', 100, 115, 3, blocks.STONE,
                 [],
                 (10, 20),
                 [
    (0.6, blocks.COAL, 70, 102, 0.4),
    (0.4, blocks.IRON, 60, 80, 0.3)
])
LAKE = Biome('lake', 30, 40, 1, blocks.SAND,
             [(blocks.SAND, 32)],
             (1, 3),
             [
    (0.7, blocks.COAL, 25, 32, 0.2),
    (0.3, blocks.IRON, 15, 20, 0.1)
])

# tuple (is_island, height, temperature, humidity)
BIOMES = {
    (1, 0, 0, 0): PLAIN,
    (1, 1, 0, 0): HILL,
    (1, 2, 0, 0): MOUNTAIN,
    (0, 0, 0, 0): LAKE
}