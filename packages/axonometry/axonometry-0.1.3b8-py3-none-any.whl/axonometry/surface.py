# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .line import Line
    from .point import Point

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Surface:
    """A collection class to apply various graphical operations on a set of lines.

    :raise AssertionError: If the geometries are not all in the same plane.
    """

    def __init__(self, lines: list[Line] | list[Point]) -> None:
        self.plane = lines
        self.key = lines
        self.lines = lines

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def is_closed(self):
        """Number of unique points equal number of lines."""
        unique_points = {point for line in self._lines for point in (line.start, line.end)}
        return len(unique_points) == len(self._lines)

    @property
    def plane(self):
        return self._plane

    @plane.setter
    def plane(self, lines: list[Line]) -> None:
        """Set the plane attribute for the surface.

        :param lines: List of lines.
        """
        planes = {obj.plane for obj in lines}
        assert len(planes) == 1, "Lines not in same plane."
        self._plane = (
            planes.pop()
        )  # Assuming the set contains only one element after the assertion passes

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, lines):
        keys = {obj.key for obj in lines}
        assert len(keys) == 1, "Lines not in same plane."
        self._key = keys.pop()

    # ==========================================================================
    # Constructors
    # ==========================================================================

    @staticmethod
    def closed(geometries: list[Line] | list[Point]) -> Surface:
        """Get surface collection of a computed continous line.

        Find missing lines from a sparse collection of lines or points. Compute new lines by
        checking nearest points of existing lines. Make a surface object from that new line
        collection.

        :param geometries: A sparse collection of :py:class:`.Point` or :py:class:`.Line`.
        """
        raise NotImplementedError

    @staticmethod
    def from_points(points: list[Point]) -> Surface:
        """Make surface from convex hull of a list of points.

        :raises NotImplementedError: WIP.
        """
        # from compas.geoemtry import convex_hull_xy
        # verts = convex_hull_xy(points)
        raise NotImplementedError

    # ==========================================================================
    # Methods
    # ==========================================================================

    def bounding_box(self):
        """Draw the axis-aligned minimum bounding box of a list of points in the plane.

        :raises NotImplementedError: WIP.
        """
        # from compas.geometry import bounding_box_xy
        # unique_points = {point for line in self._lines for point in (line.start, line.end)}
        # corners = bounding_box_xy(list(unique_points))
        raise NotImplementedError
