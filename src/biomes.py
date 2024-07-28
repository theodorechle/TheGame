import blocks
from tree import Tree

class Biome:
    def __init__(self,
                name: str,
                min_height: int,
                max_height: int,
                max_height_difference: int,
                blocks_by_zone: list[tuple[blocks.Block, int, int]],
                ore_veins_qty: tuple[int, int],
                ore_veins_repartition: list[tuple[float, blocks.Block, int, int, float]],
                tree: Tree|None = None
                ) -> None:

        self.name = name
        self.min_height = min_height
        self.max_height = max_height
        self.max_height_difference = max_height_difference
        # (block, min_height, max_size of the block stack)
        self.blocks_by_zone = blocks_by_zone
        # (min_qty, max_qty)
        self.ore_veins_qty = ore_veins_qty
        # (probability, block, min_height, max_height, probability_to_expand)
        self.ore_veins_repartition = ore_veins_repartition
        self.tree = tree


def get_biome_environment_values(biome: Biome) -> tuple[int, int, int]|None:
    for vars, biome_ in BIOMES.items():
        if biome_ == biome:
            return vars
    return None

PLAIN = Biome(
    name='plain',
    min_height=40,
    max_height=50,
    max_height_difference=1,
    blocks_by_zone=[
        (blocks.GRASS, 40, 1),
        (blocks.EARTH, 35, 10)
    ],
    ore_veins_qty=(2, 10),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 20, 50, 0.4),
        (0.4, blocks.IRON, 16, 47, 0.3)
    ],
    tree = Tree(trunk_block=blocks.WOOD,
                leave_block=blocks.LEAVES,
                min_trunk_height=5,
                max_trunk_height=6,
                min_leaves_height=1,
                max_leaves_height=3,
                min_leaves_width=1,
                max_leaves_width=3,
                tree_spawn_chance=0.1,
                forest_spawn_chance=0.3,
                stay_forest_chance=0.7,
                grows_in=blocks.AIR
                )
)

HILL = Biome(
    name='hill',
    min_height=60,
    max_height=65,
    max_height_difference=2,
    blocks_by_zone=[
        (blocks.GRASS, 50, 1),
        (blocks.EARTH, 40, 10)
    ],
    ore_veins_qty=(4, 10),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 30, 60, 0.4),
        (0.4, blocks.IRON, 25, 57, 0.3)
    ],
    tree = Tree(trunk_block=blocks.WOOD,
                leave_block=blocks.LEAVES,
                min_trunk_height=5,
                max_trunk_height=6,
                min_leaves_height=1,
                max_leaves_height=3,
                min_leaves_width=1,
                max_leaves_width=3,
                tree_spawn_chance=0.1,
                forest_spawn_chance=0.3,
                stay_forest_chance=0.7,
                grows_in=blocks.AIR
                )
)

MOUNTAIN = Biome(
    name='mountain',
    min_height=80,
    max_height=90,
    max_height_difference=3,
    blocks_by_zone=[],
    ore_veins_qty=(10, 20),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 30, 80, 0.4),
        (0.4, blocks.IRON, 20, 65, 0.3)
    ]
)

HIGH_MOUNTAIN = Biome(
    name='high-mountain',
    min_height=100,
    max_height=115,
    max_height_difference=3,
    blocks_by_zone=[(blocks.SNOW, 100, 3)],
    ore_veins_qty=(10, 20),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 30, 102, 0.4),
        (0.4, blocks.IRON, 40, 80, 0.3)
    ]
)

LAKE = Biome(
    name='lake',
    min_height=20,
    max_height=30,
    max_height_difference=1,
    blocks_by_zone=[],
    ore_veins_qty=(1, 3),
    ore_veins_repartition=[
        (0.7, blocks.COAL, 15, 22, 0.2),
        (0.3, blocks.IRON, 5, 10, 0.1)
    ]
)

# tuple (height, temperature, humidity)
BIOMES = {
    (0, 1, 1): PLAIN,
    (1, 1, 1): HILL,
    (2, 1, 1): MOUNTAIN,
    (3, 1, 1): HIGH_MOUNTAIN,
    (-1, 1, 1): LAKE
}