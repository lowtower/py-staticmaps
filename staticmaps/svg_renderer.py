"""py-staticmaps - SvgRenderer"""

# py-staticmaps
# Copyright (c) 2022 Florian Pigorsch; see /LICENSE for licensing information

import base64
import math
import typing

import s2sphere  # type: ignore
import svgwrite  # type: ignore

from .color import BLACK, WHITE, Color
from .renderer import Renderer
from .transformer import Transformer

if typing.TYPE_CHECKING:
    # avoid circlic import
    from .object import Object  # pylint: disable=cyclic-import


class SvgRenderer(Renderer):
    """An svg image renderer class that extends a generic renderer class"""

    def __init__(self, transformer: Transformer) -> None:
        Renderer.__init__(self, transformer)
        self._draw = svgwrite.Drawing(
            size=(f"{self._trans.image_width()}px", f"{self._trans.image_height()}px"),
            viewBox=f"0 0 {self._trans.image_width()} {self._trans.image_height()}",
        )
        clip = self._draw.defs.add(self._draw.clipPath(id="page"))
        clip.add(self._draw.rect(insert=(0, 0), size=(self._trans.image_width(), self._trans.image_height())))
        self._group: typing.Optional[svgwrite.container.Group] = None

    def drawing(self) -> svgwrite.Drawing:
        """Return the svg drawing for the image

        Returns:
            svgwrite.Drawing: svg drawing
        """
        return self._draw

    def group(self) -> svgwrite.container.Group:
        """Return the svg group for the image

        Returns:
            svgwrite.container.Group: svg group
        """
        assert self._group is not None
        return self._group

    def render_objects(
        self,
        objects: typing.List["Object"],
        tighten: bool,
    ) -> None:
        """Render all objects of static map

        Parameters:
            objects (typing.List["Object"]): objects of static map
            tighten (bool): tighten to boundaries
        """
        self._group = self._draw.g(clip_path="url(#page)")
        x_count = math.ceil(self._trans.image_width() / (2 * self._trans.world_width()))
        for obj in objects:
            for p in range(-x_count, x_count + 1):
                group = self._draw.g(clip_path="url(#page)", transform=f"translate({p * self._trans.world_width()}, 0)")
                obj.render_svg(self)
                self._group.add(group)
        objects_group = self._tighten_to_boundary(self._group, objects, tighten)
        self._draw.add(objects_group)
        self._group = None

    def render_background(self, color: typing.Optional[Color]) -> None:
        """Render background of static map

        Parameters:
            color (typing.Optional[Color]): background color
        """
        if color is None:
            return
        group = self._draw.g(clip_path="url(#page)")
        group.add(self._draw.rect(insert=(0, 0), size=self._trans.image_size(), rx=None, ry=None, fill=color.hex_rgb()))
        self._draw.add(group)

    def render_tiles(
        self,
        download: typing.Callable[[int, int, int], typing.Optional[bytes]],
        objects: typing.List["Object"],
        tighten: bool,
    ) -> None:
        """Render tiles of static map

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]): url of tiles provider
            objects (typing.List["Object"]): objects of static map
            tighten (bool): tighten to boundaries
        """
        self._group = self._draw.g(clip_path="url(#page)")
        for yy in range(0, self._trans.tiles_y()):
            y = self._trans.first_tile_y() + yy
            if y < 0 or y >= self._trans.number_of_tiles():
                continue
            for xx in range(0, self._trans.tiles_x()):
                x = (self._trans.first_tile_x() + xx) % self._trans.number_of_tiles()
                try:
                    tile_img = self.fetch_tile(download, x, y)
                    if tile_img is None:
                        continue
                    self._group.add(
                        self._draw.image(
                            tile_img,
                            insert=(
                                int(xx * self._trans.tile_size() + self._trans.tile_offset_x()),
                                int(yy * self._trans.tile_size() + self._trans.tile_offset_y()),
                            ),
                            size=(self._trans.tile_size(), self._trans.tile_size()),
                        )
                    )
                except RuntimeError:
                    pass
        tiles_group = self._tighten_to_boundary(self._group, objects, tighten)
        self._draw.add(tiles_group)
        self._group = None

    def _tighten_to_boundary(
        self, group: svgwrite.container.Group, objects: typing.List["Object"], tighten: bool = False
    ) -> svgwrite.container.Group:
        """Calculate scale and offset for tight rendering on the boundary

        Parameters:
            group (svgwrite.container.Group): svg group
            objects (typing.List["Object"]): objects of static map
            tighten (bool): tighten to boundaries
        Returns:
            svgwrite.container.Group: svg group
        """
        # pylint: disable=too-many-locals
        if not tighten:
            return group

        # boundary points
        bounds = self.get_object_bounds(objects)
        nw_x, nw_y = self._trans.ll2pixel(s2sphere.LatLng.from_angles(bounds.lat_lo(), bounds.lng_lo()))
        se_x, se_y = self._trans.ll2pixel(s2sphere.LatLng.from_angles(bounds.lat_hi(), bounds.lng_hi()))
        # boundary size
        size_x = se_x - nw_x
        size_y = nw_y - se_y
        # scale to boundaries
        width = self._trans.image_width()
        height = self._trans.image_height()
        # scale = 1, if division by zero
        try:
            scale_x = size_x / width
            scale_y = size_y / height
            scale = 1 / max(scale_x, scale_y)
        except ZeroDivisionError:
            scale = 1
        # translate new center to old center
        off_x = -0.5 * width * (scale - 1)
        off_y = -0.5 * height * (scale - 1)
        # finally, translate and scale
        group.translate(off_x, off_y)
        group.scale(scale)
        return group

    def render_attribution(self, attribution: typing.Optional[str]) -> None:
        """Render attribution from given tiles provider

        Parameters:
            attribution (typing.Optional[str]:): Attribution for the given tiles provider
        """
        if (attribution is None) or (attribution == ""):
            return
        group = self._draw.g(clip_path="url(#page)")
        group.add(
            self._draw.rect(
                insert=(0, self._trans.image_height() - 12),
                size=(self._trans.image_width(), 12),
                rx=None,
                ry=None,
                fill=WHITE.hex_rgb(),
                fill_opacity="0.8",
            )
        )
        group.add(
            self._draw.text(
                attribution,
                insert=(2, self._trans.image_height() - 3),
                font_family="Arial, Helvetica, sans-serif",
                font_size="9px",
                fill=BLACK.hex_rgb(),
            )
        )
        self._draw.add(group)

    def fetch_tile(
        self, download: typing.Callable[[int, int, int], typing.Optional[bytes]], x: int, y: int
    ) -> typing.Optional[str]:
        """Fetch tiles from given tiles provider

        Parameters:
            download (typing.Callable[[int, int, int], typing.Optional[bytes]]):
                callable
            x (int): width
            y (int): height

        Returns:
            typing.Optional[str]: svg drawing
        """
        image_data = download(self._trans.zoom(), x, y)
        if image_data is None:
            return None
        return SvgRenderer.create_inline_image(image_data)

    @staticmethod
    def guess_image_mime_type(data: bytes) -> str:
        """Guess mime type from image data

        Parameters:
            data (bytes): image data

        Returns:
            str: mime type
        """
        if data[:4] == b"\xff\xd8\xff\xe0" and data[6:11] == b"JFIF\0":
            return "image/jpeg"
        if data[1:4] == b"PNG":
            return "image/png"
        return "image/png"

    @staticmethod
    def create_inline_image(image_data: bytes) -> str:
        """Create an svg inline image

        Parameters:
            image_data (bytes): Image data

        Returns:
            str: svg inline image
        """
        image_type = SvgRenderer.guess_image_mime_type(image_data)
        return f"data:{image_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
