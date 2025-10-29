#!/usr/bin/env python

"""py-staticmaps - Example Frankfurt-New York"""
# Copyright (c) 2020-2025 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_ArcGISWorldImagery)

warsaw = staticmaps.create_latlng(52.233207, 21.061419)
frankfurt = staticmaps.create_latlng(50.110644, 8.682092)
newyork = staticmaps.create_latlng(40.712728, -74.006015)
los_angeles = staticmaps.create_latlng(33.999099, -118.411735)

context.add_object(staticmaps.Line([frankfurt, newyork], color=staticmaps.BLUE, width=4))
context.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))

# render png via pillow
image = context.render_pillow(800, 500)
image.save("frankfurt_newyork.pillow.png")

# render anti-aliased png (this only works if pycairo is installed)
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("frankfurt_newyork.cairo.png")

# render svg
svg_image = context.render_svg(800, 500)
with open("frankfurt_newyork.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render png via pillow - tight boundaries
context.set_tighten_to_bounds(True)
image = context.render_pillow(800, 500)
image.save("frankfurt_newyork.tight.pillow.png")

# render png via cairo - tight boundaries
if staticmaps.cairo_is_supported():
    context.set_tighten_to_bounds(True)
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("frankfurt_newyork.tight.cairo.png")

# render svg - tight boundaries
context.set_tighten_to_bounds(True)
svg_image = context.render_svg(800, 500)
with open("frankfurt_newyork.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

context2 = staticmaps.Context()
context2.set_tile_provider(staticmaps.tile_provider_CartoDarkNoLabels)
context2.add_object(staticmaps.Marker(frankfurt, color=staticmaps.GREEN, size=12))
context2.add_object(staticmaps.Marker(newyork, color=staticmaps.RED, size=12))
context2.add_object(staticmaps.Bounds([warsaw, los_angeles]))

# render svg
svg_image = context2.render_svg(800, 500)
with open("frankfurt_newyork.warsaw_los_angeles_bounds.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)

# render svg - tight boundaries
context2.set_tighten_to_bounds(True)
svg_image = context2.render_svg(800, 500)
with open("frankfurt_newyork.warsaw_los_angeles_bounds.tight.svg", "w", encoding="utf-8") as f:
    svg_image.write(f, pretty=True)
