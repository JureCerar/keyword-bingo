# Keyword Bingo

Generate a keyword bingo card

## Installation

Type the following in command line:

```bash
git clone https://github.com/JureCerar/keyword-bingo.git
cd ./keyword-bingo
pip install .
```

__NOTE:__ Before installation you can edit default bingo keywords by editing `bingo/bingo.dat`.

## Usage

```
usage: bingo [-h] [-V] [-i INPUT] [-o OUTPUT] [-n SIZE] [-s SEED]

Generate a keyword bingo card.

options:
  -h, --help                  show this help message and exit
  -V, --version               show version information and exit
  -i INPUT, --input INPUT     input file with bingo words (one per line)
  -o OUTPUT, --output OUTPUT  output picture file
  -n SIZE, --size SIZE        size of the bingo card
  -s SEED, --seed SEED        random number generator seed
```

## License

This program is licensed under the __GNU General Public License v3.0__

Copyright (C) 2024 [Jure Cerar](https://github.com/JureCerar)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.