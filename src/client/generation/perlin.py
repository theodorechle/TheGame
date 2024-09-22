import numpy as np
import random

class Perlin:
    def __init__(self, seed: str, scale: float, frequency: float, amplitude: float, octaves: int, persistence: float, lacunarity: float, grid_size: int=256) -> None:
        self.seed = seed
        self.scale = scale
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

    # Gradient function (returns the gradient based on a hash of the grid point)
    @staticmethod
    def gradient(h, x):
        # Random gradient: either 1 or -1
        g = 1 if h % 2 == 0 else -1
        return g * x

    # A permutation table to create random gradient selection
    def generate_permutation_table(self):
        state = random.getstate()
        random.seed(self.seed)
        self.permutation_table = list(range(self.grid_size))
        random.shuffle(self.permutation_table)
        random.setstate(state)

    # Perlin noise function for 1D with a permutation table
    def perlin(self, x):
        # Determine the grid cell coordinates
        x0 = int(x) & (self.grid_size - 1)
        x1 = (x0 + 1) & (self.grid_size - 1)

        # Local coordinate within the grid cell
        sx = x - x0

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

    # Generate 1D Perlin noise with octaves
    def generate(self, x: int):
        total = 0
        amplitude = 1
        frequency = self.frequency
        max_amplitude = 0

        for _ in range(self.octaves):
            i = x / self.scale * frequency
            total += self.perlin(i) * amplitude
            max_amplitude += amplitude

            amplitude *= self.persistence  # Reduce amplitude for the next octave
            frequency *= self.lacunarity   # Increase frequency for the next octave

        # Normalize the result by the maximum amplitude
        if max_amplitude > 0:
            total /= max_amplitude
        
        # Clamp the result to be within [-amplitude, amplitude]
        return max(-self.amplitude, min(total * self.amplitude, self.amplitude))

    # Generate a range of 1D Perlin noise
    def generate_range(self, length: int):
        state = random.getstate()
        random.seed(self.seed)
        
        noise = np.zeros(length)
        for i in range(length):
            noise[i] = self.generate(i)
        
        random.setstate(state)
        return noise

if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # Parameters for the terrain generation
    length = 200  # Length of the map (number of points)
    scale = 20.0  # Adjust scale to zoom in/out on the noise
    frequency = 1.0  # Adjust the frequency to control the number of features
    amplitude = 20.0  # Adjust the amplitude to control the height of the terrain
    octaves = 3  # Number of octaves
    persistence = 0.5  # How much each successive octave contributes (lower values -> smoother)
    lacunarity = 2.0  # How much the frequency increases for each octave

    seed = '476211806'  # Use a seed to get the same random terrain for testing (remove for full randomness)

    # Generate the 1D Perlin noise terrain with adjustable frequency, amplitude, and octaves
    perlin = Perlin(seed, scale, frequency, amplitude, octaves, persistence, lacunarity)
    terrain = perlin.generate_range(length)

    # Plot the generated terrain
    plt.plot(terrain)
    plt.title(f"1D Perlin Noise Terrain\nFrequency={frequency}, Amplitude={amplitude}, Octaves={octaves}")
    plt.show()
