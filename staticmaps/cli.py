#!/usr/bin/env python
"""py-staticmaps - cli.py - entry point"""

# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import argparse
import enum
import os

import staticmaps


class FileFormat(enum.Enum):
    """FileFormat"""

    GUESS = "guess"
    PNG = "png"
    SVG = "svg"


def determine_file_format(file_format: FileFormat, file_name: str) -> FileFormat:
    """
    determine_file_format Try to determine the file format

    Parameters:
        file_format (FileFormat): The File Format
        file_name (str): The file name

    Raises:
        RuntimeError: If the file format cannot be determined

    Returns:
        FileFormat: A FileFormat object
    """
    if file_format != FileFormat.GUESS:
        return file_format
    extension = os.path.splitext(file_name)[1]
    if extension == ".png":
        return FileFormat.PNG
    if extension == ".svg":
        return FileFormat.SVG
    raise RuntimeError("Cannot guess the image type from the given file name: {file_name}")


def main() -> None:
    """main Entry point"""
    args_parser = argparse.ArgumentParser(prog="createstaticmap")
    args_parser.add_argument(
        "--center",
        metavar="LAT,LNG",
        type=str,
    )
    args_parser.add_argument(
        "--zoom",
        metavar="ZOOM",
        type=int,
    )
    args_parser.add_argument(
        "--width",
        metavar="WIDTH",
        type=int,
        required=True,
    )
    args_parser.add_argument(
        "--height",
        metavar="HEIGHT",
        type=int,
        required=True,
    )
    args_parser.add_argument(
        "--background",
        metavar="COLOR",
        type=str,
    )
    args_parser.add_argument(
        "--marker",
        metavar="LAT,LNG",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--line",
        metavar="LAT,LNG LAT,LNG ...",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--area",
        metavar="LAT,LNG LAT,LNG ...",
        type=str,
        action="append",
    )
    args_parser.add_argument(
        "--bounds",
        metavar="LAT,LNG LAT,LNG",
        type=str,
    )
    args_parser.add_argument(
        "--tight-to-bounds",
        action="store_true",
        default=False,
        help="Tighten static map to minimum boundaries of objects, custom boundaries, ...(default: False)",
    )
    args_parser.add_argument(
        "--tiles",
        metavar="TILEPROVIDER",
        type=str,
        choices=staticmaps.default_tile_providers.keys(),
        default=staticmaps.tile_provider_OSM.name(),
    )
    args_parser.add_argument(
        "--tiles-api-key",
        dest="tiles_api_key",
        metavar="API_KEY",
        type=str,
        default=None,
    )
    args_parser.add_argument(
        "--file-format",
        metavar="FORMAT",
        type=FileFormat,
        choices=FileFormat,
        default=FileFormat.GUESS,
    )
    args_parser.add_argument(
        "filename",
        metavar="FILE",
        type=str,
        nargs=1,
    )

    args = args_parser.parse_args()

    context = staticmaps.Context()

    context.set_tile_provider(staticmaps.default_tile_providers[args.tiles], args.tiles_api_key)

    if args.center is not None:
        context.set_center(staticmaps.parse_latlng(args.center))
    if args.zoom is not None:
        context.set_zoom(args.zoom)
    if args.background is not None:
        context.set_background_color(staticmaps.parse_color(args.background))
    if args.area:
        for coords in args.area:
            context.add_object(staticmaps.Area(staticmaps.parse_latlngs(coords)))
    if args.line:
        for coords in args.line:
            context.add_object(staticmaps.Line(staticmaps.parse_latlngs(coords)))
    if args.marker:
        for coords in args.marker:
            context.add_object(staticmaps.Marker(staticmaps.parse_latlng(coords)))
    if args.bounds is not None:
        context.add_object(staticmaps.Bounds(staticmaps.parse_latlngs(args.bounds)))
    context.set_tighten_to_bounds(args.tighten_to_bounds)

    file_name = args.filename[0]
    if determine_file_format(args.file_format, file_name) == FileFormat.PNG:
        image = context.render_cairo(args.width, args.height)
        image.write_to_png(file_name)
    else:
        svg_image = context.render_svg(args.width, args.height)
        with open(file_name, "w", encoding="utf-8") as f:
            svg_image.write(f, pretty=True)
    print(f"wrote result image to {file_name}")


if __name__ == "__main__":
    main()
