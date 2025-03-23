# Copyright (C) 2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Halftone subcommand."""

import argparse
import logging
import math

from PIL import Image, ImageDraw

from fotolab import save_gif_image, save_image

log = logging.getLogger(__name__)


def build_subparser(subparsers) -> None:
    """Build the subparser."""
    halftone_parser = subparsers.add_parser(
        "halftone", help="halftone an image"
    )

    halftone_parser.set_defaults(func=run)

    halftone_parser.add_argument(
        dest="image_filenames",
        help="set the image filename",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_FILENAMES",
    )

    halftone_parser.add_argument(
        "-ba",
        "--before-after",
        default=False,
        action="store_true",
        dest="before_after",
        help="generate a GIF showing before and after changes",
    )

    halftone_parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    halftone_parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )


def run(args: argparse.Namespace) -> None:
    """Run halftone subcommand.

    Args:
        args (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    log.debug(args)

    for image_filename in args.image_filenames:
        original_image = Image.open(image_filename)
        halftone_image = create_halftone_image(original_image)

        if args.before_after:
            save_gif_image(
                args,
                image_filename,
                original_image,
                halftone_image,
                "halftone",
            )
        else:
            save_image(args, halftone_image, image_filename, "halftone")


def create_halftone_image(
    original_image: Image.Image, cell_count: int = 50
) -> Image.Image:
    """Create a halftone version of the input image.

    Modified from the circular halftone effect processing.py example from
    https://tabreturn.github.io/code/processing/python/2019/02/09/processing.py_in_ten_lessons-6.3-_halftones.html

    Args:
        original_image: The source image to convert
        cell_count: Number of cells across the width (default: 50)

    Returns:
        Image.Image: The halftone converted image
    """
    grayscale_image = original_image.convert("L")
    width, height = original_image.size

    halftone_image = Image.new("L", (width, height), "black")
    draw = ImageDraw.Draw(halftone_image)

    cellsize = width / cell_count
    rowtotal = math.ceil(height / cellsize)

    for row in range(rowtotal):
        for col in range(cell_count):
            # Calculate center point of current cell
            x = int(col * cellsize + cellsize / 2)
            y = int(row * cellsize + cellsize / 2)

            # Get brightness and calculate dot size
            brightness = grayscale_image.getpixel((x, y))
            dot_size = 10 * brightness / 200

            # Draw the dot
            draw.ellipse(
                [
                    x - dot_size / 2,
                    y - dot_size / 2,
                    x + dot_size / 2,
                    y + dot_size / 2,
                ],
                fill=255,
            )

    return halftone_image
