from chunk_manager import Chunk

class MapGenerator:
    def __init__(self, biomes_files_path, structures_files_path) -> None:
        self.biomes_files_path = biomes_files_path
        self.structures_files_path = structures_files_path
        self.get_biomes()
        self.get_structures()

    def get_biomes(self):
        ...
    
    def get_structures(self):
        ...