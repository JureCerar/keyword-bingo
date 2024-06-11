#!/usr/bin/env python3
#
# Copyright (C) 2024 Jure Cerar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random
import time
import hashlib
import argparse
import pathlib
from typing import Tuple

import numpy as np

from PIL import Image, ImageDraw, ImageFont


__author__ = "Jure Cerar"
__date__ = "11 Jun 2024"
__version__ = "0.1.0"


# Global settings
SIZE = 200  # Size of each field
PADDING = 5  # Padding on each side
FONT_SIZE = 25 # Default font size
FONT_PATH = "arial.ttf"  # Path to font file
INPUT = "bingo.dat" # Default words input file


def text_size(draw: ImageDraw, text: str, font: str) -> Tuple[float, float]:
    """Get size of text in pixels"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def text_box(size, padding, text, font_size, font_path):
    """
    DESCRIPTION
        Generate a text box using Pillow. Text is split and resized to fit
        the canvas.
    ARGUMENTS
        size = int: Size of canvas in pixels.
        padding = int: Number of pixels between content and border.
        text = str: Text do display. Will be split and resized to fit canvas.
        font_path = str: Font to use for drawing.
    """
    # Create a blank image with white background
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)

    # Load a font
    current_font_size = font_size  # Starting font size
    font = ImageFont.truetype(font_path, current_font_size)

    # Function to wrap text
    def wrap_text(text, font, max_width):
        lines = []
        for line in text.split('\n'):
            # Textwrap calculates line width in characters, but we need it in pixels
            words = line.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if text_size(draw, test_line, font)[0] <= max_width:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            lines.append(' '.join(current_line))
        return lines

    # Adjust font size to fit text within the square with padding
    max_text_width = size - 2 * padding
    while True:
        wrapped_text = wrap_text(text, font, max_text_width)
        text_height = sum([text_size(draw, line, font)[1]
                          for line in wrapped_text])
        if text_height <= (size - 2 * padding):
            break
        current_font_size -= 1
        font = ImageFont.truetype(font_path, current_font_size)

    # Calculate position to center the text
    total_text_height = sum([text_size(draw, line, font)[1]
                            for line in wrapped_text])
    y = (size - total_text_height) // 2

    for line in wrapped_text:
        text_width, text_height = text_size(draw, line, font)
        x = (size - text_width) // 2
        # Ensure the text doesn't go outside the left padding
        x = max(x, padding)
        draw.text((x, y), line, fill="black", font=font)
        y += text_height

    # Optional: Draw the border of the square
    draw.rectangle([0, 0, size-1, size-1], outline="black")

    return image


def draw_star(size, points, outer_radius, inner_radius, color):
    """
    DESCRIPTION
        Draw a star using Pillow
    ARGUMENTS
        size = int: Size of canvas in pixels.
        points = int: Number of points on a star.
        outer_radius = int: Outer radius of star.
        inner_radius = int: Inner radius of star.
        color = any: Star fill color.
    """
    # Create a blank image with white background
    image = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(image)

    # Center of canvas
    center = size // 2

    # Calculate the coordinates of the star points
    angle = 360 / (points * 2)
    coordinates = []

    for i in range(points * 2):
        radius = outer_radius if i % 2 == 0 else inner_radius
        x = center + radius * np.cos(np.radians(angle * i))
        y = center - radius * np.sin(np.radians(angle * i))
        coordinates.append((x, y))

    # Draw the star
    draw.polygon(coordinates, fill=color)

    # Draw the border of the square
    draw.rectangle([0, 0, size-1, size-1], outline="black")

    return image


def read_words(filename: str) -> Tuple[list, str]:
    """Read words from file and calculate md5 sum of file"""
    hash = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    with open(filename) as handle:
        words = handle.read().splitlines()
    return words, hash


def _bingo(rows, cols, grid, seed, hash, *, size=SIZE, padding=PADDING, font_size=FONT_SIZE, font_path=FONT_PATH):
    """Generate cols x row sized bingo card"""

    # Create a blank image with white background
    image = Image.new('RGB', (cols*size, rows*size), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Add each bingo tile individually
    for i in range(cols):
        for j in range(rows):
            if (i, j) == (cols // 2, rows // 2):
                # Bingo tile
                radius = size // 2 - padding
                box = draw_star(size, 5, radius, 0.5 * radius, "gold")
            else:
                # Normal tile
                box = text_box(size, padding, grid[i, j], font_size, font_path)

            # Add tile to image
            image.paste(box, (i * size, j * size))

    # Add random seed and hash in bottom left corner
    line = f"seed: {seed} md5: {hash}"
    font = ImageFont.truetype(font_path, 12)
    height = text_size(draw, line, font=font)[1]
    xy = (padding, rows * size - padding - int(height * 1.5))
    draw.text(xy, line, fill="gray", font=font)

    return image


def bingo(input, output=None, rows=5, cols=5, seed=None):
    """
    DESCRIPTION
        Generate keyword bing card
    USAGE
        bingo input [, output [, rows [, cols [, seed ]]]]
    ARGUMENTS
        input = str: Input file with bingo words (one per line).
        output = str: Output image name. {default: None}
        rows = int: Number of rows. {default: 5}
        cols = int: Number of columns. {default: 5}
        seed = any: Random number generator seed. {default: None}
    """
    if rows < 1 or cols < 1:
        raise Exception(f"Invalid size: {rows} x {cols}")

    # Initialize random
    if not seed:
        seed = int(time.time())
    random.seed(seed)

    # Read and shuffle dictionary
    words, hash = read_words(input)
    words = sorted(words, key=lambda x: random.random())

    # Check if there is enough words
    if len(words) < cols * rows:
        raise Exception(f"Not enough words in list: <{cols * rows}")

    # Arrange words in a grid
    grid = np.array(words[:cols*rows]).reshape((cols, rows))

    # Generate bingo card
    image = _bingo(rows, cols, grid, seed, hash)

    # Save to file
    if output:
        image.save(output)

    # Display to screen
    image.show()


def main():

    # Default input file
    path = pathlib.Path(__file__).resolve().parent
    input_file = pathlib.Path.joinpath(path, INPUT)

    # Define command line arguments
    parser = argparse.ArgumentParser(
        description="Generate a keyword bingo card.",
        epilog=f"%(prog)s {__version__}",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog,
            max_help_position=32
        ), 
    )
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"%(prog)s {__version__}",
        help="show version information and exit"
    )
    parser.add_argument(
        "-i", "--input", dest="input", type=str, default=input_file,
        help="input file with bingo words (one per line)"
    )
    parser.add_argument(
        "-o", "--output", dest="output", type=str, default=None,
        help="output picture file"
    )
    parser.add_argument(
        "-n", "--size", dest="size", type=int, default=5,
        help="size of the bingo card"
    )
    parser.add_argument(
        "-s", "--seed", dest="seed", default=None,
        help="random number generator seed"
    )
    args = parser.parse_args()

    # Let's do this 
    bingo(args.input, args.output, args.size, args.size, args.seed)


if __name__ == "__main__":
    main()
