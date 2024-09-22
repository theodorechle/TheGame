import numpy as np
import random

class Perlin:
    def __init__(self, seed: str, frequency: float, amplitude: float, octaves: int, persistence: float, lacunarity: float, grid_size: int=1024) -> None:
        self.seed = seed
        self.frequency = frequency
        self.amplitude = amplitude
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.grid_size = grid_size
        self.generate_permutation_table()

    @staticmethod
    def fade(t):
        return t ** 3 * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp(t, a, b):
        return a + t * (b - a)

    @staticmethod
    def gradient(h, x):
        g = 1 if h % 2 == 0 else -1
        return g * x

    def generate_permutation_table(self):
        state = random.getstate()
        random.seed(self.seed)
        self.permutation_table = list(range(self.grid_size))
        random.shuffle(self.permutation_table)
        random.setstate(state)

    def perlin(self, x):
        # Handle negative coordinates by ensuring consistent wrapping
        x0 = int(np.floor(x)) & (self.grid_size - 1)
        x1 = (x0 + 1) & (self.grid_size - 1)

        # Local coordinate inside the grid
        sx = x - np.floor(x)

        # Hash coordinates of the grid corners using the permutation table
        h0 = self.permutation_table[x0 % self.grid_size]
        h1 = self.permutation_table[x1 % self.grid_size]

        # Gradient vectors at the corners
        n0 = self.gradient(h0, sx)
        n1 = self.gradient(h1, sx - 1)

        # Fade the local coordinate
        u = self.fade(sx)

        # Interpolate between the two corners
        return self.lerp(u, n0, n1)

    def generate(self, x: int):
        total = 0
        amplitude = 1
        frequency = self.frequency
        max_amplitude = 0

        for _ in range(self.octaves):
            i = x * frequency
            total += self.perlin(i) * amplitude
            max_amplitude += amplitude

            amplitude *= self.persistence
            frequency *= self.lacunarity

        if max_amplitude > 0:
            total /= max_amplitude
        
        return total * self.amplitude

    def generate_range(self, start: int, length: int):
        noise = np.zeros(length)
        for i in range(length):
            noise[i] = self.generate(start + i)
        return noise

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    length = 10000
    frequency = 0.001
    amplitude = 256
    octaves = 3
    persistence = 0.1
    lacunarity = 2.0

    seed = 'azertyui'

    perlin = Perlin(seed, frequency, amplitude, octaves, persistence, lacunarity)
    
    # Generating range that includes negative numbers
    terrain = perlin.generate_range(-length // 2, length)

    # Plot the generated terrain
    plt.plot(terrain)
    plt.title(f"1D Infinite Perlin Noise Terrain\nFrequency={frequency}, Amplitude={amplitude}, Octaves={octaves}")
    plt.show()
