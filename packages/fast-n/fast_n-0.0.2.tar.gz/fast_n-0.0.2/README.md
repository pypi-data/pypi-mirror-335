***Fast_n*** is a fast and easy to use python library to generate noise. **(It currently only supports perlin noise.)**

## Installation

Type `pip install fast_n` in your command prompt to install ***fast_n***. If you do not have python installed, download it on the [official website](https://www.python.org/downloads/).

## Use cases

Noise is very useful for anything procedural, being especially used for procedural world generation in video games. ***Fast_n*** is fast enough for most use cases.

## Features

At the moment, only perlin noise is implemented but I'm sure I'll add more at some point, and I already plan on improving the speed of the noise generation by writing it in C rather than pure python.

## How to use

Create a noise object, passing in a seed and some noise-dependant parameters, then call its Sample() method with x and y 2D coordinates to access the value at the given position.

This exemple shows how to draw perlin noise using ***PIL*** to handle the image stuff:

```python
from fastn import noise
from PIL import Image

perlin = noise.PerlinNoise(23) # creates a PerlinNoise object with a seed of 23
img = Image.new("L", (128, 128)) # creates an image using only a grayscale channel
for y in range(128):
    for x in range(128):
        # with perlin noise you want to avoid only using integer coordinates 
        # because they always return the same value
        noiseValue = perlin.Sample(x / 32, y / 32)
        pixelBrightness = round((noiseValue * 0.5 + 0.5) * 255) # transforms the output from a [-1, 1] range to a [0, 255] range
        img.putpixel((x, y), pixelBrightness)
img.show() # opens the image in an image viewer
```

## Credits

- [Raouf](https://rtouti.github.io/): My perlin noise implementation is based on [this blog post](https://rtouti.github.io/graphics/perlin-noise-algorithm) he made.