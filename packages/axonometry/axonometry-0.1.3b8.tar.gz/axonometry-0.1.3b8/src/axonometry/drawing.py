# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal

from compas.geometry import Geometry as CGeometry
from compas.geometry import Line as CLine
from compas.geometry import Point as CPoint
from compas.geometry import Polyline as CPolyline
from shapely import LineString
from vpype import Document, LineCollection, circle, read_svg

from .config import config_manager

if TYPE_CHECKING:
    import compas
    from PIL.Image import Image

    from .axonometry import Axonometry
    from .line import Line
    from .point import Point


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Drawing:
    """Records all drawing and projection operations to be rendered.

    A wrapper class for :py:class:`vpype.Document` and :py:class:`compas.scene.Scene`.
    Instantiated in :py:attr:`Axonometry.drawing`.
    Methods mostly called with the ``add_*()`` methods at the :py:class:`Plane` level.

    .. attention::

        On user-level, geometries are added to :py:class:`Plane` objects, ex. with
        :py:meth:`Plane.draw_line`. Because the necessary updates of the plane and geometry
        metadata (i.e. :py:attr:`Plane.objects`, :py:attr:`Line.projections`, etc.) is handled
        by these upstream functions.
    """

    def __init__(
        self,
        page_size: Literal["A1"] | tuple[float, float] = "A1",
        orientation: str = "portrait",
    ) -> None:
        self.dimensions = (
            (
                config_manager.config["sizes"][page_size][orientation][0]
                * config_manager.config["css_pixel"],
                config_manager.config["sizes"][page_size][orientation][1]
                * config_manager.config["css_pixel"],
            )
            if isinstance(page_size, str)
            else page_size
        )
        self.document: Document = Document(
            page_size=self.dimensions,
        )
        self.frames = None

    def __repr__(self) -> str:
        """Identify drawing."""
        return "Drawing"  # + hex(id(self)) ?

    # ==========================================================================
    # Methods
    # ==========================================================================

    def record_frames(self):
        from vpype_viewer import render_image

        self.frames: list[Image] = [render_image(self.document, size=(1920, 1080))]

    def add(self, item: Point | Line, layer_id: int | None = None) -> None:
        """Add a :py:class:`Point` or :py:class:`Line` to embedded :py:class:`vpype.Document`.

        Pass :py:attr:`Point.data` and :py:attr:`Line.data` to
        :py:meth:`add_compas_geometry`.

        :param layer_id: Define the layer number for the added geometry, usually
          handled upstream.
        """
        compas_data = [item.data]  # it's the compas data which is being drawn
        logger.debug(f"[{item.key.upper()}] {item} added to {self}.")
        self.add_compas_geometry(compas_data, layer_id=layer_id)

    def add_axonometry(
        self,
        axonometry: Axonometry,
        position: tuple[float, float] | None = None,
    ) -> None:
        """Combine several instances of :py:class:`Axonometry`.

        .. caution::

            Not fully implemented yet.

        >>> from axonometry import Axonometry, Drawing
        >>> drawing = Drawing()
        >>> axo1 = Axonometry(47.5, 15)
        >>> axo2 = Axonometry(30, 30)
        >>> drawing.add_axonometry(axo1)
        >>> drawing.add_axonometry(axo2)

        """
        if position:
            axonometry.drawing.document.translate()  # TODO compute translate from new position
        self.document.extend(axonometry.drawing.document)

    def add_compas_geometry(
        self,
        compas_data: list[
            compas.geometry.Line | compas.geometry.Point | compas.geometry.Polyline
        ],
        layer_id: int | None = None,
    ) -> None:
        """Add a compas :py:class:`~compas.geometry.Point` or :py:class:`~compas.geometry.Line` collection to embedded :py:class:`vpype.Document`.

        Converts a list of :py:class:`compas.geometry.Point` and
        :py:class:`compas.geometry.Line` into a :py:class:`vpype.LineCollection`.
        Then added to the :py:class:`vpype.Document`.

        :param compas_data: Add :py:class:`compas.geometry.Point` and
          :py:class:`compas.geometry.Line` objects directly, or receive the attributes
          :py:attr:`Point.data` and :py:attr:`Line.data` when calling :py:meth:`Drawing.add`.
        :param layer_id: Define the layer number for the added geometry, usually
          handled upstream.
        """
        # no traces ?
        logger.debug(f"[{self}] Add compas data objects to drawing: {compas_data}")
        # for item in compas_data:
        #     self.viewer.scene.add(item)
        geometry = convert_compas_to_vpype_lines(compas_data)
        if geometry:
            geometry.translate(self.dimensions[0] / 2, self.dimensions[1] / 2)
            self.document.add(geometry, layer_id=layer_id)
            if self.frames:
                from vpype_viewer import render_image

                self.frames.append(render_image(self.document, size=(1920, 1080)))


# ==========================================================================
# Utilities
# ==========================================================================


def convert_compas_to_vpype_lines(
    compas_geometries: list[CGeometry],
) -> LineCollection:
    """Convert a list of compas geometries to a vpype :py:class:`vpype.LineCollection`."""
    vpype_lines = LineCollection()
    for compas_geometry in compas_geometries:
        shapely_line = _convert_compas_to_shapely(compas_geometry)
        vpype_lines.append(shapely_line)
    return vpype_lines


def _convert_compas_to_shapely(compas_geometry: CGeometry) -> LineString:
    """Convert a compas geometry object to a shapely LineString."""
    if isinstance(compas_geometry, CLine):
        return LineString(
            [
                (
                    compas_geometry.start.x * config_manager.config["css_pixel"],
                    compas_geometry.start.y * config_manager.config["css_pixel"],
                ),
                (
                    compas_geometry.end.x * config_manager.config["css_pixel"],
                    compas_geometry.end.y * config_manager.config["css_pixel"],
                ),
            ],
        )
    if isinstance(compas_geometry, CPolyline):
        return LineString(
            [
                (
                    point.x * config_manager.config["css_pixel"],
                    point.y * config_manager.config["css_pixel"],
                )
                for point in compas_geometry
            ],
        )
    if isinstance(compas_geometry, CPoint):
        if config_manager.config["point_radius"]:
            return circle(
                compas_geometry.x * config_manager.config["css_pixel"],
                compas_geometry.y * config_manager.config["css_pixel"],
                config_manager.config["point_radius"],
            )
        return None
    raise ValueError(f"Unsupported Compas geometry type: {compas_geometry}")


def _convert_svg_vpype_doc(svg_file: str) -> Document:
    """Create a vpype Document from a list of Compas geometries."""
    coll = read_svg(svg_file, 0.01)[0].as_mls()
    points = []
    for line in coll.geoms:
        for coord in line.coords:
            points.append(coord)

    compas_geometries = [CPolyline(points)]
    layers = convert_compas_to_vpype_lines(compas_geometries)
    document = Document()
    for layer in layers:
        document.add(layer, layer_id=1)  # Assuming all lines are on the same layer
    return document
