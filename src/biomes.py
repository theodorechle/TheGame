import json

class Biome:
    PATH = 'resources/biomes'
    def __init__(self, name) -> None:
        self.name = name
        self.infos = None

    def load(self) -> None:
        with open(f'{self.PATH}/{self.name}.json') as f:
            self.infos = json.load(f)