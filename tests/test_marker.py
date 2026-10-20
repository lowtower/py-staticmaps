"""py-staticmaps - Test Marker"""

# Copyright (c) 2020-2026 Florian Pigorsch & Contributors. All rights reserved. See /LICENSE for licensing information

import staticmaps


def test_creation() -> None:
    staticmaps.Marker(staticmaps.create_latlng(48, 8), color=staticmaps.YELLOW, size=8)


def test_bounds() -> None:
    marker = staticmaps.Marker(staticmaps.create_latlng(48, 8))
    assert marker.bounds().is_point()
