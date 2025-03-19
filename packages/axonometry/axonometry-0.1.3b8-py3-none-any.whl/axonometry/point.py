# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Literal

from compas.geometry import Line as CLine
from compas.geometry import Point as CPoint
from compas.geometry import intersection_line_line_xy

from .config import config_manager

if TYPE_CHECKING:
    import compas

    from .axonometry import Axonometry
    from .plane import ReferencePlane

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Point:
    """The atoms of geometry.

    The coordinates have to be passed on explicitly::

        Point(x=10, y=20)
        Point(z=15, y=20)
        Point(x=10, z=15)
        Point(x=10, y=20, z=15)

    :param kwargs: A minimum of two coordanate values.
    :raises ValueError: A point is described by a minimum of two coordinates.

    """

    @property
    def __data__(self) -> list:
        """Give access to data in order to be used with compas methods.

        .. warning::

            The data is very different from the user defined values.
            They are all compas.geometry objects with only (X,Y)
            coordinates, all in the same plane (i.e. your piece of
            paper).

        """
        return list(self.data.__data__)

    def __init__(self, **kwargs: float) -> None:
        self.plane: ReferencePlane | Axonometry = None
        """The :py:class:`Plane` of which the line is in; set by parent."""
        self.matrix_applied: bool = False  # Flag set when point added to reference plane
        self.projections: dict[Literal["xy", "yz", "zx", "xyz"], Point | list[Point]] = {
            "xy": None,
            "yz": None,
            "zx": None,
            "xyz": [],
        }  #: Collection of the lines' projections; updated automatically.
        self._set_coordinates(**kwargs)
        self.key: Literal["xy", "yz", "zx", "xyz"] = self._set_key()
        """"The points' coordinate system, i.e. plane membership."""
        # Data is the point location on the paper
        self.data: compas.geometry.Point | None = None  #: View plane coordinate system point.
        if self.key in ["xy", "yz", "zx"]:
            self.reset_data()

    def __repr__(self) -> str:
        """Get the user set coordinate values."""
        if self.key == "xy":
            repr_str = f"Point(x={self.x:.2f}, y={self.y:.2f})"
        elif self.key == "yz":
            repr_str = f"Point(y={self.y:.2f}, z={self.z:.2f})"
        elif self.key == "zx":
            repr_str = f"Point(x={self.x:.2f}, z={self.z:.2f})"
        else:
            repr_str = f"Point(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"

        return repr_str

    def __eq__(self, other: Point) -> bool:
        """Projected points are considered as equal."""
        if (not isinstance(other, type(self))) or (self is None or other is None):
            # if the other item of comparison is not also of the Point class
            return False
        if self.key == other.key:
            return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)
        common_key = "".join(set(self.key).intersection(other.key))
        if set(common_key) == set("xy"):
            return (self.x == other.x) and (self.y == other.y)
        if set(common_key) == set("yz"):
            return (self.y == other.y) and (self.z == other.z)
        if set(common_key) == set("zx"):
            return (self.x == other.x) and (self.z == other.z)
        return False

    # ==========================================================================
    # Properties
    # ==========================================================================

    def _set_coordinates(self, **kwargs: float) -> None:
        """Set the coordinates from the provided kwargs."""
        if len(kwargs) == 1:
            # If only one coordinate is provided, raise an error.
            raise ValueError("At least two coordinates must be provided.")
        self.x = kwargs.get("x")
        self.y = kwargs.get("y")
        self.z = kwargs.get("z")

    def _set_key(self) -> Literal["xy", "yz", "zx", "xyz"]:
        combined_key = ""
        if self.x is not None:
            combined_key += "x"
        if self.y is not None:
            combined_key += "y"
        if self.z is not None:
            combined_key += "z"
        # Flip letters in last case
        return "zx" if combined_key == "xz" else combined_key

    # ==========================================================================
    # Constructors
    # ==========================================================================

    @staticmethod
    def from_xy(x: float, y: float) -> Point:
        """Create a new Point instance with the given x and y coordinates.

        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.

        :returns: A new Point instance with the specified x and y coordinates.
        """
        return Point(x=x, y=y)

    @staticmethod
    def from_yz(y: float, z: float) -> Point:
        """Create a new Point instance with the given y and z coordinates.

        :param y: The y-coordinate of the point.
        :param z: The z-coordinate of the point.

        :returns: A new Point instance with the specified y and z coordinates.
        """
        return Point(y=y, z=z)

    @staticmethod
    def from_zx(z: float, x: float) -> Point:
        """Create a new Point instance with the given z and x coordinates.

        :param x: The z-coordinate of the point.
        :param y: The x-coordinate of the point.

        :returns: A new Point instance with the specified z and x coordinates.
        """
        return Point(z=z, x=x)

    @staticmethod
    def from_xyz(x: float, y: float, z: float) -> Point:
        """Create a new Point instance with the given x, y, and z coordinates.

        :param x: The x-coordinate of the point.
        :param y: The y-coordinate of the point.
        :param z: The z-coordinate of the point.

        :returns: A new Point instance with the specified x, y, and z coordinates.
        """
        return Point(x=x, y=y, z=z)

    @staticmethod
    def random_point(key: Literal["xy", "yz", "zx", "xyz"] = "xyz") -> Point:
        """Get a random point.

        To follow architecture standards, z is always equal or higher than 0.
        """
        return {
            "xy": Point.from_xy(random.randint(-20, 70), random.randint(-20, 70)),  # noqa: S311
            "yz": Point.from_yz(random.randint(-20, 70), random.randint(0, 80)),  # noqa: S311
            "zx": Point.from_zx(random.randint(0, 80), random.randint(-20, 70)),  # noqa: S311
            "xyz": Point.from_xyz(
                random.randint(-20, 70),  # noqa: S311
                random.randint(-20, 70),  # noqa: S311
                random.randint(0, 80),  # noqa: S311
            ),
        }.get(key)

    # ==========================================================================
    # Methods
    # ==========================================================================

    def reset_data(self) -> CPoint:
        """Reset point data.

        Function used to add objects a second time to a reference plane.
        Data needs a reset because by adding a point to a reference plane, the point.data is
        transformed with the planes matrix. This process is automated with the
        help of the :py:attr:`axonometry.Point.matrix_applied` boolean flag attribute.
        """
        if self.key == "xy":
            self.data = CPoint(self.x, self.y)
        elif self.key == "yz":
            self.data = CPoint(self.z, self.y)
        elif self.key == "zx":
            self.data = CPoint(self.x, self.z)
        else:
            self.data: CPoint | None = None
        return self.data

    # ==========================================================================
    # Projection
    # ==========================================================================

    def project(
        self,
        distance: float | None = None,
        ref_plane_key: Literal["xy", "yz", "zx"] | None = None,
        auxilaray_plane_key: Literal["xy", "yz", "zx"] | None = None,
    ) -> Point:
        """Project current point on another plane.

        .. note::

            As modifying a :py:class:`Line` is basically handling its points, this method is
            extensively called in :py:meth:`draw_line` and :py:meth:`~Line.project`, with the
            points :py:attr:`Line.start` and :py:attr:`Line.end` as parameters.

        Two scenarios: current point is in a reference plane and is projected onto the
        axonometric picture plane. Or the current point is in the axonometric picture
        plane and is beeing projected on a reference plane. Depending, the right paramteres
        have to be provided.

        :param distance: The missing third coordinate in order to project the point on the
            axonometric picture plane. This applies when the point to project is contained
            in a reference plane.
        :param ref_plane_key: The selected reference plane on which to project the point. This
            applies when the point to project is on the axonometric picture plane.
        """
        # determine projection origin plane
        if self.plane.key == "xyz":
            logger.debug(f"{self} is in XYZ and projected on a reference plane")
            new_point = self._project_on_reference_plane(ref_plane_key)
        else:
            logger.debug(
                f"{self} is in {self.plane} and projected on a reference plane",
            )
            new_point = self._project_on_axonometry_plane(distance, auxilaray_plane_key)

        return new_point

    def _project_on_axonometry_plane(
        self,
        distance: float,
        auxilaray_plane_key: Literal["xy", "yz", "zx"] | None = None,
    ) -> Point:
        """Projection initiated from a reference plane onto the axonometry plane.

        In order to determine the axonometric point an auxilary point in a second reference
        plane is created. The projected intersection of the current and the auxilary
        point are the axonometric point.

        For the auxilary plane choice, the XY plane is privileged when possible
        because of architecture standards.
        """
        assert distance is not None, (
            "Provide (third coordinate value) in order to project the point into XYZ space."
        )
        if self.plane.key == "xy":
            new_point = Point(x=self.x, y=self.y, z=distance)  # data will be update

            if auxilaray_plane_key and auxilaray_plane_key not in ["yz", "zx"]:
                # If provided, ensure the auxiliary plane key is valid.
                raise ValueError(
                    f"{auxilaray_plane_key} invalid for a projection from {self.plane}",
                )
            if not auxilaray_plane_key:
                # If no auxiliary plane key is provided, randomly choose one from "yz" and "zx"
                auxilaray_plane_key = random.choice(["yz", "zx"])  # noqa: S311

            if auxilaray_plane_key == "yz":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(y=self.y, z=distance),
                )
            elif auxilaray_plane_key == "zx":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(x=self.x, z=distance),
                )

        elif self.plane.key == "yz":
            new_point = Point(x=distance, y=self.y, z=self.z)  # data will be update

            if auxilaray_plane_key and auxilaray_plane_key not in ["zx", "xy"]:
                # If provided, ensure the auxiliary plane key is valid.
                raise ValueError(
                    f"{auxilaray_plane_key} invalid for a projection from {self.plane}",
                )
            if not auxilaray_plane_key:
                # If no auxiliary plane key is provided, randomly choose one from "xy" and "zx"
                auxilaray_plane_key = "xy"  # random.choice(["zx", "xy"])

            if auxilaray_plane_key == "zx":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(z=self.z, x=distance),
                )
            elif auxilaray_plane_key == "xy":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(y=self.y, x=distance),
                )

        elif self.plane.key == "zx":
            new_point = Point(x=self.x, y=distance, z=self.z)  # data will be update

            if auxilaray_plane_key and auxilaray_plane_key not in ["xy", "yz"]:
                raise ValueError(
                    f"{auxilaray_plane_key} invalid for a projection from {self.plane}",
                )
            if not auxilaray_plane_key:
                auxilaray_plane_key = "xy"  # random.choice(["xy", "yz"])

            if auxilaray_plane_key == "xy":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(x=self.x, y=distance),
                )
            elif auxilaray_plane_key == "yz":
                auxilary_point = self.plane.axo[auxilaray_plane_key].draw_point(
                    Point(z=self.z, y=distance),
                )

        axo_point_data = intersection_line_line_xy(
            CLine.from_point_and_vector(self.data, self.plane.projection_vector),
            CLine.from_point_and_vector(
                auxilary_point.data,
                self.plane.axo[auxilaray_plane_key].projection_vector,
            ),
        )

        new_point.data = CPoint(*axo_point_data)
        # draw intersection
        self.plane.drawing.add_compas_geometry(
            [
                CLine(self.data, axo_point_data),
                CLine(auxilary_point.data, axo_point_data),
            ],
            layer_id=config_manager.config["layers"]["projection_traces"]["id"],
        )

        self.plane.axo.draw_point(new_point)

        # Update point projections collection
        pair_projections_points(new_point, auxilary_point)
        pair_projections_points(new_point, self)

        return new_point

    def _project_on_reference_plane(self, ref_plane_key: Literal["xy", "yz", "zx"]) -> Point:
        if self == self.projections[ref_plane_key]:
            # projection of point already exists, nothing to do
            logger.debug(
                f"{self=} is already projected in {ref_plane_key.upper()}: {self.projections[ref_plane_key]=}",
            )
            new_point = self.projections[ref_plane_key]

        else:
            if ref_plane_key == "xy":
                # Point was maybe already projected when added to the XYZ axo space
                new_point = self.plane[ref_plane_key].draw_point(
                    Point(x=self.x, y=self.y),
                )
            elif ref_plane_key == "yz":
                # Point was maybe already projected when added to the XYZ axo space
                new_point = self.plane[ref_plane_key].draw_point(
                    Point(y=self.y, z=self.z),
                )
            elif ref_plane_key == "zx":
                # Point was maybe already projected when added to the XYZ axo space
                new_point = self.plane[ref_plane_key].draw_point(
                    Point(x=self.x, z=self.z),
                )

            # draw new projection line
            self.plane.drawing.add_compas_geometry(
                [CLine(self.data, new_point.data)],
                layer_id=config_manager.config["layers"]["projection_traces"]["id"],
            )
            pair_projections_points(self, new_point)

        return new_point

    def project_into_axo_line(
        self,
        distance: float,
        length: float,
        ref_plane_keys: list[Literal["xy", "yz", "zx"]] | None = None,
    ):
        """Projection of a line in axonometric picture plane out of its perpendicular point.

        Instead of building a point, one adds a line in axo space.

        >>> p_xy.project_into_axo_line(distance=80, length=50)
        INFO:axonometry.plane:[XYZ] Add Line(Point(x=24, y=38, z=105.0), Point(x=24, y=38, z=55.0))
        >>> p_yz.project_into_axo_line(distance=80, length=50)
        INFO:axonometry.plane:[XYZ] Add Line(Point(x=105.0, y=29, z=51), Point(x=55.0, y=29, z=51))
        >>> p_zx.project_into_axo_line(distance=80, length=50)
        INFO:axonometry.plane:[XYZ] Add Line(Point(x=17, y=105.0, z=26), Point(x=17, y=55.0, z=26))

        :param distance: The position of the middle of the new line.
        :param length: The length of the new line.

        :return: A new :py:class:`Line` on the axonometric picture plane.
        """
        from .line import Line  # local import because of cicularity

        # Make new line points
        if self.key == "xy":
            far = Point(x=self.x, y=self.y, z=distance + length / 2)
            close = Point(x=self.x, y=self.y, z=distance - length / 2)
        elif self.key == "yz":
            far = Point(y=self.y, z=self.z, x=distance + length / 2)
            close = Point(y=self.y, z=self.z, x=distance - length / 2)
        elif self.key == "zx":
            far = Point(z=self.z, x=self.x, y=distance + length / 2)
            close = Point(z=self.z, x=self.x, y=distance - length / 2)

        # Add line to axo plane
        new_line = Line(close, far)
        new_line = self.plane.axo.draw_line(new_line, ref_plane_keys=ref_plane_keys)
        # Get updated point data
        close = new_line.start
        far = new_line.end
        # Draw projection trace
        self.plane.drawing.add_compas_geometry(
            [CLine(self.data, close.data)],
            layer_id=config_manager.config["layers"]["projection_traces"]["id"],
        )
        # Pair projections
        pair_projections_points(self, close)
        pair_projections_points(self, far)
        new_line.projections[self.key] = self

        return new_line

    def on_projection_planes(self) -> list[str] | None:
        """Get the plane keys in which point has a projection."""
        return [key for key in self.projections if self.projections[key] is not None]

    def not_on_projection_planes(self) -> list[str] | None:
        """Get the plane keys in which point has no projection."""
        return [key for key in self.projections if self.projections[key] is None]


# ==========================================================================
# Predicates
# ==========================================================================


def is_coplanar(points: list[Point]) -> bool:
    """Check if a series of points are in the same plane."""
    keys = [point.key for point in points]
    return len(set(keys)) == 1


# ==========================================================================
# Utilities
# ==========================================================================


def pair_projections_points(obj1: Point, obj2: Point) -> None:
    """Include each other in the projections collection."""
    if obj2.key == "xyz":
        obj1.projections["xyz"].append(obj2)
    else:
        obj1.projections[obj2.key] = obj2
    if obj1.key == "xyz":
        obj2.projections["xyz"].append(obj1)
    else:
        obj2.projections[obj1.key] = obj1
