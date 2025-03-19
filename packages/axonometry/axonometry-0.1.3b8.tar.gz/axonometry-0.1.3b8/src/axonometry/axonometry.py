# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import math
import pathlib
from typing import TYPE_CHECKING, Literal

from .config import config_manager
from .drawing import Drawing
from .plane import Plane, ReferencePlane
from .trihedron import Trihedron, random_valid_angles

if TYPE_CHECKING:
    from compas.geometry import Vector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Axonometry(Plane):
    """Axonometry by intersection setup.

    This class helps to set up the axonometry. From there one can start to use its
    method to add geometries (mostly :py:class:`Line`).

    To set up the necessary projection planes, the class first instatiates a
    :py:class:`Trihedron` object which calculates the :term:`tilt <Tilt>` to produce the three
    :py:class:`ReferencePlane` objects. These, and the :py:class:`Axonometry` can then be used
    to draw, i.e. :py:meth:`~Plane.draw_line`.

    As an attribute, this class instantiates a :py:class:`Drawing` object which collects, or
    so to say records, all the drawing and projection operations (:py:meth:`~Plane.draw_line`,
    :py:meth:`~Line.project`).

    .. note::

        When adding objects, and they have only two of the x y z, it means they are projecitons
        in a reference plane.

    :param angles: Architectural notation axonometry angle pair.
    :param trihedron_position: Position of trihedron on the paper.
    :param ref_planes_distance: Reference plane transolation distance.
    :param trihedron_size: Coordinate axes size.
    """

    def __init__(
        self,
        *angles: float,
        ref_planes_distance: float = 100.0,
        trihedron_size: float = 100.0,
        trihedron_position: tuple[float, float] = (0, 0),
        page_size: Literal["A1"] | tuple[float, float] = "A1",
        orientation: str = "portrait",
    ) -> None:
        super().__init__()  # Access methods of the parent class
        Plane.drawing = Drawing(
            page_size=page_size,
            orientation=orientation,
        )
        """Instantiate Drawing object for all Plane objects."""
        ReferencePlane.axo = self
        """Attribute this Axonometry object to all ReferencePlane objects."""
        self.key = "xyz"
        logger.info(f"[AXONOMETRY] {angles[0]}°/{angles[1]}°")
        self._trihedron = Trihedron(
            tuple(angles),
            position=trihedron_position,
            size=trihedron_size,
            ref_planes_distance=ref_planes_distance,
        )

        Plane.drawing.add_compas_geometry(
            self._trihedron.axes.values(),
            layer_id=config_manager.config["layers"]["axo_system"]["id"],
        )
        for plane in self._trihedron.reference_planes.values():
            Plane.drawing.add_compas_geometry(
                plane.axes,
                layer_id=config_manager.config["layers"]["axo_system"]["id"],
            )

    def __repr__(self) -> str:
        """Get axonometry values in standard horizon angle notation."""
        return f"Axonometry {math.degrees(self._trihedron.axo_angles[0]):.2f}°/{math.degrees(self._trihedron.axo_angles[1]):.2f}°"

    def __getitem__(self, item: str) -> ReferencePlane:
        """Select a reference plane by key."""
        if item in self._trihedron.reference_planes:
            return self._trihedron.reference_planes[item]
        return self

    # ==========================================================================
    # Properties
    # ==========================================================================

    @property
    def x(self) -> Vector:
        """X coordinate vector."""
        return self._trihedron.axes["x"].direction

    @property
    def y(self) -> Vector:
        """Y coordinate vector."""
        return self._trihedron.axes["y"].direction

    @property
    def z(self) -> Vector:
        """Z coordinate vector."""
        return self._trihedron.axes["z"].direction

    @property
    def xy(self) -> ReferencePlane:
        """Get the Axonometry's XY :py:class:`.ReferencePlane` object."""
        return self._trihedron.reference_planes["xy"]

    @property
    def yz(self) -> ReferencePlane:
        """Get the Axonometry's YZ :py:class:`.ReferencePlane` object."""
        return self._trihedron.reference_planes["yz"]

    @property
    def zx(self) -> ReferencePlane:
        """Get the Axonometry's ZX :py:class:`.ReferencePlane` object."""
        return self._trihedron.reference_planes["zx"]

    # ==========================================================================
    # Constructors
    # ==========================================================================

    @staticmethod
    def random_angles(
        trihedron_position: tuple[float, float] = (0, 0),
        ref_planes_distance: float = 100.0,
        trihedron_size: float = 100.0,
        page_size: Literal["A1"] | tuple[float, float] = "A1",
        orientation: str = "portrait",
    ) -> Axonometry:
        """Generate valid axonometric angles and initialize the Axonometry object."""
        angles = random_valid_angles()
        return Axonometry(
            *angles,
            trihedron_position=trihedron_position,
            ref_planes_distance=ref_planes_distance,
            trihedron_size=trihedron_size,
            page_size=page_size,
            orientation=orientation,
        )

    # ==========================================================================
    # Methods
    # ==========================================================================

    def save_png(self, filename: str, directory: str = "./output/") -> str:
        """Save drawing to PNG file.

        This function first makes an SVG file (cropped) with :py:meth:`save_svg`.
        Then converts it with :py:meth:`cairosvg.svg2png`.

        :param filename: Name of the PNG file.
        :param directory: Path to directory, defaults to ``./output/``.
        :returns: The relative filepath of the saved file.
        """
        from cairosvg import svg2png

        # Convert SVG file to PNG file
        svg = self.save_svg("_tmp_" + filename, crop=True)
        # with pathlib.Path.open(, "w") as f:
        svg2png(url=svg, write_to=directory + filename + ".png")

        return directory + filename + ".png"

    def save_svg(
        self,
        filename: str,
        directory: str = "./output/",
        *,
        crop: bool = False,
        center: bool = False,
    ) -> str:
        """Save drawing to file SVG.

        :param filename: Name of the SVG file.
        :param directory: Path to directory, defaults to ``./output/``.
        :param crop: Reduze page size to fit geometry, with small border.
        :param center: Center geometry on page.
        :returns: The relative filepath of the saved file.
        """
        from vpype import write_svg

        page_size = self.drawing.document.page_size  # i.e. default page size

        if crop:
            # reduce to minimum size
            self.drawing.document.fit_page_size_to_content()
            # add borders
            page_size = (
                self.drawing.document.page_size[0] + 100,
                self.drawing.document.page_size[1] + 100,
            )
            # make borders equal by centering geometry
            center = True

        with pathlib.Path.open(directory + filename + ".svg", "w") as f:
            write_svg(
                output=f,
                document=self.drawing.document,
                page_size=page_size,
                center=center,
                color_mode="layer",  # use "none" for black
            )

        return directory + filename + ".svg"

    def save_gif(self, filename: str, directory: str = "./output/"):
        image0 = self.drawing.frames[0]
        image0.save(
            directory + filename + ".gif",
            save_all=True,
            append_images=self.drawing.frames[1:],
            duration=100,
            loop=0,
        )

    def _save_json(self, filename: str, directory: str = "./output/") -> None:
        """Save drawing data to json file."""
        try:
            with pathlib.Path.open(directory + filename + ".json", "w") as f:
                Plane.drawing.scene.to_json(f, pretty=False)
        except FileExistsError:
            logger.info("Already exists.")

    def show_paths(self) -> None:
        """Show the drawing paths with the vpype viewer."""
        # move geometry into center of page
        # TODO: this breaks the use of drawing.extend !
        # prevents from calling the function while script is executed.
        from vpype_cli import execute

        command = (
            config_manager.config["layers"]["axo_system"]["vp_cli"]
            + " "
            + config_manager.config["layers"]["projection_traces"]["vp_cli"]
            + " "
            + config_manager.config["layers"]["geometry"]["vp_cli"]
        )
        execute(
            f"{command} show",
            document=self.drawing.document,
        )

    def visualize(self) -> None:
        """Not Implemented."""
        raise NotImplementedError

    def import_obj_file(
        self,
        filepath: str,
        scale_factor: int = 50,
    ) -> None:
        from compas.datastructures import Mesh
        from compas.files import OBJ
        from compas.geometry import Scale

        from .line import Line
        from .point import Point

        obj = OBJ(filepath)
        obj.read()
        mesh = Mesh.from_vertices_and_faces(obj.vertices, obj.faces)
        mesh.transform(Scale.from_factors(3 * [scale_factor]))
        lines = mesh.to_lines()
        logger.info(f"[OBJ] Load mesh: {mesh.number_of_edges()} edges to draw.")

        for line in lines:
            self.draw_line(
                Line(
                    Point(x=line[0][0], y=line[0][1], z=line[0][2]),
                    Point(x=line[1][0], y=line[1][1], z=line[1][2]),
                ),
            )

    def record_frames(self) -> None:
        """Toggle recording of frames at each modification of geometry."""
        logger.info("[GIF] Start frame recording.")
        logger.warning(
            "[GIF] Expect heavy performance loss: for each geometry a new image is saved",
        )
        self.drawing.record_frames()
