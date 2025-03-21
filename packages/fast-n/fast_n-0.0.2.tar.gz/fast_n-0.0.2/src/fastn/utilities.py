import random

# ────────────────── LISTS ──────────────────

def Shuffle(rand: random.Random, table: list[int]) -> None:
    """Shuffles a table using a Random object."""
    
    for j in range(len(table) - 1, 0, -1):
        i = rand.randint(0, j - 1)
        table[j], table[i] = table[i], table[j]

# ────────────────── MATH ──────────────────

def Dot(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Dot product between two 2D vectors (represented as tuples)."""
    
    return (a[0] * b[0] + a[1] * b[1])

def Fade(t: float) -> float:
    """Easing function used for the perlin noise."""
    
    return ((6 * t - 15) * t + 10) * t * t * t

def Lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two numbers."""
    
    return a + t * (b - a)