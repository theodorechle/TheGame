import blocks

class Tree:
    def __init__(self,
                trunk_block: blocks.Block,
                leave_block: blocks.Block,
                min_trunk_height: int,
                max_trunk_height: int,
                min_leaves_height: int,
                max_leaves_height: int,
                min_leaves_width: int,
                max_leaves_width: int,
                tree_spawn_chance: float,
                forest_spawn_chance: float,
                stay_forest_chance: float,
                grows_in: blocks.Block
                ) -> None:
        self.trunk_block = trunk_block
        self.leave_block = leave_block
        self.min_trunk_height = min_trunk_height
        self.max_trunk_height = max_trunk_height
        self.min_leaves_height = min_leaves_height
        self.max_leaves_height = max_leaves_height
        self.min_leaves_width = min_leaves_width
        self.max_leaves_width = max_leaves_width
        self.tree_spawn_chance = tree_spawn_chance
        self.forest_spawn_chance = forest_spawn_chance
        self.stay_forest_chance = stay_forest_chance
        self.grows_in = grows_in

class Biome:
    def __init__(self,
                name: str,
                min_height: int,
                max_height: int,
                max_height_difference: int,
                upper_block: blocks.Block,
                blocks_by_zone: list[tuple[blocks.Block, int]],
                ore_veins_qty: tuple[int, int],
                ore_veins_repartition: list[tuple[float, blocks.Block, int, int, float]],
                tree: Tree = None
                ) -> None:

        self.name = name
        self.min_height = min_height
        self.max_height = max_height
        self.max_height_difference = max_height_difference
        self.upper_block = upper_block
        # (block, min_height, (max_size of the block stack))
        self.blocks_by_zone = blocks_by_zone
        # (min_qty, max_qty)
        self.ore_veins_qty = ore_veins_qty
        # (probability, block, min_height, max_height, probability_to_expand)
        self.ore_veins_repartition = ore_veins_repartition
        self.tree = tree


def get_biome_environment_values(biome: Biome) -> tuple[int, int, int, int]|None:
    for vars, biome_ in BIOMES.items():
        if biome_ == biome:
            return vars
    return None

PLAIN = Biome(
    name='plain',
    min_height=50,
    max_height=60,
    max_height_difference=1,
    upper_block=blocks.GRASS,
    blocks_by_zone=[(blocks.EARTH, 40, 10)],
    ore_veins_qty=(2, 10),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 30, 40, 0.4),
        (0.4, blocks.IRON, 26, 37, 0.3)
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
    max_height=80,
    max_height_difference=2,
    upper_block=blocks.GRASS,
    blocks_by_zone=[(blocks.EARTH, 50, 10)],
    ore_veins_qty=(4, 10),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 50, 60, 0.4),
        (0.4, blocks.IRON, 45, 57, 0.3)
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
    min_height=100,
    max_height=115,
    max_height_difference=3,
    upper_block=blocks.STONE,
    blocks_by_zone=[],
    ore_veins_qty=(10, 20),
    ore_veins_repartition=[
        (0.6, blocks.COAL, 70, 102, 0.4),
        (0.4, blocks.IRON, 60, 80, 0.3)
    ]
)

LAKE = Biome(
    name='lake',
    min_height=30,
    max_height=40,
    max_height_difference=1,
    upper_block=blocks.STONE,
    blocks_by_zone=[],
    ore_veins_qty=(1, 3),
    ore_veins_repartition=[
        (0.7, blocks.COAL, 25, 32, 0.2),
        (0.3, blocks.IRON, 15, 20, 0.1)
    ]
)

# tuple (height, temperature, humidity)
BIOMES = {
    (0, 1, 1): PLAIN,
    (1, 1, 1): HILL,
    (2, 1, 1): MOUNTAIN,
    (-1, 1, 1): LAKE
}