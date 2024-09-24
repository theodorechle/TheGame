from blocks import Block

class Tree:
    def __init__(self,
                trunk_block: Block,
                leave_block: Block,
                min_trunk_height: int,
                max_trunk_height: int,
                min_leaves_height: int,
                max_leaves_height: int,
                min_leaves_width: int,
                max_leaves_width: int,
                tree_spawn_chance: float,
                forest_spawn_chance: float,
                stay_forest_chance: float,
                grows_in: Block
                ) -> None:
        self.trunk_block = trunk_block
        self.leaves_block = leave_block
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
