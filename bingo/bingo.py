#!/usr/bin/env python3
#
# Copyright (C) 2024-2025 Jure Cerar
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
import argparse
import pathlib
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


__author__ = "Jure Cerar"
__contact__ = "name.surname@gmail.com"
__url__ = "https://github.com/JureCerar/keyword-bingo"
__date__ = "15 Jun 2024"
__version__ = "0.2.0"


# Global settings
SIZE = 200  # [px] Size of each field
PADDING = 5  # [px] Padding on each side
FONT_SIZE = 25  # [px] Default font size
FONT_PATH = "arial.ttf"  # Path to font file
INPUT = "bingo.dat" # Default words input file
COLORS = {
    "background": "white",
    "text": "black",
    "star": "gold",
    "border": "gray",
    "footer": "gray",
}


def text_size(draw: ImageDraw, text: str, font: str) -> Tuple[float, float]:
    """Get size of text in pixels"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def text_box(size: int, padding: int, text: str) -> Image:
    """
    Generate a text box using Pillow. Text is split and resized to fit
    the canvas.
    Args:
        size (int): Size of canvas in pixels.
        padding (int): Number of pixels between content and border.
        text (str): Text do display. Will be split and resized to fit canvas.
        font_size (int): Sie of the font used.
        font_path (str): Font to use for drawing.
    """
    # Create a blank image with white background
    image = Image.new("RGB", (size, size), color=COLORS["background"])
    draw = ImageDraw.Draw(image)

    # Load a font at current size, we will shrink it as needed to fit in a tile
    current_font_size = FONT_SIZE  # Starting font size
    font = ImageFont.truetype(FONT_PATH, current_font_size)

    # Function to wrap text
    def wrap_text(text, font, max_width):
        lines = []
        for line in text.split("\n"):
            # Textwrap calculates line width in characters, but we need it in pixels
            words = line.split()
            current_line = []
            for word in words:
                test_line = " ".join(current_line + [word])
                if text_size(draw, test_line, font)[0] <= max_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            lines.append(" ".join(current_line))
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
        font = ImageFont.truetype(FONT_PATH, current_font_size)

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

    # Draw the border of the square
    draw.rectangle([0, 0, size-1, size-1], outline=COLORS["border"], width=1)

    return image


def draw_star(size: int, points: int, outer_radius: int, inner_radius: int) -> Image:
    """Draw a star using Pillow
    Args:
        size (int): Size of canvas in pixels.
        points (int): Number of points on a star.
        outer_radius (int): Outer radius of star.
        inner_radius (int): Inner radius of star.
    """
    # Create a blank image with white background
    image = Image.new("RGB", (size, size), COLORS["background"])
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

    # Draw the star tile
    draw.polygon(coordinates, fill=COLORS["star"])
    draw.rectangle([0, 0, size-1, size-1], outline=COLORS["border"])

    return image


def _bingo(rows: int, cols: int, grid: np.ndarray, footer: str) -> Image:
    """Generate cols x row sized bingo card"""

    # Create a blank image with white background
    image = Image.new("RGB", (cols * SIZE, rows * SIZE), COLORS["background"])
    draw = ImageDraw.Draw(image)

    # Add tiles to bingo card 
    for i in range(cols):
        for j in range(rows):
            # Middle tile is bingo tile
            if (i, j) == (cols // 2, rows // 2):
                radius = SIZE // 2 - PADDING
                box = draw_star(SIZE, 5, radius, 0.5 * radius)
            else:
                box = text_box(SIZE, PADDING, grid[i, j])
            image.paste(box, (i * SIZE, j * SIZE))

    # Add footer in the bottom left corner
    if footer:
        font = ImageFont.truetype(FONT_PATH, 12)
        height = text_size(draw, str(footer), font=font)[1]
        xy = (PADDING, rows * SIZE - PADDING - int(height * 1.5))
        draw.text(xy, str(footer), fill=COLORS["footer"], font=font)

    return image


def bingo(words: list[str], rows: int = 5, cols: int = 5, seed: int|float|str = None) -> Image:
    """Generate keyword bing card
    Args:
        input (list): Input file with bingo words (one per line).
        rows (int): Number of rows. {default: 5}
        cols (int): Number of columns. {default: 5}
        seed (int, float, str): Random number generator seed. {default: None}
    Returns:
        result (PIL.Image): Pillow Image object with bing card
    """
    if rows < 1 or cols < 1:
        raise Exception(f"Invalid size: {rows} x {cols}")
    if len(words) < cols * rows:
        raise Exception(f"Not enough words in list: <{cols * rows}")
    
    if not seed:
        seed = int(time.time())
    random.seed(seed)
    footer = f"Seed: {seed}"

    # Shuffle words and put them onto a grid
    shuffled = sorted(words, key=lambda x: random.random())
    grid = np.array(shuffled[:cols*rows]).reshape((cols, rows))

    return _bingo(rows, cols, grid, footer)


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
        "-s", "--seed", dest="seed", type=int, default=None,
        help="random number generator seed"
    )
    args = parser.parse_args()

    # Read input file
    with open(args.input, "r") as f:
        words = f.read().splitlines() 

    # Let's do this 
    img = bingo(words, args.size, args.size, args.seed)

    # Display and save image
    if args.output:
        img.save(args.output)
    img.show()


if __name__ == "__main__":
    main()
