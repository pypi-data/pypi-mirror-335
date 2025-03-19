# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import math
from typing import Literal

from compas.geometry import Frame as CFrame
from compas.geometry import Line as CLine
from compas.geometry import Point as CPoint
from compas.geometry import Transformation as CTransformation
from compas.geometry import Translation as CTranslation
from compas.geometry import Vector as CVector

from .plane import ReferencePlane

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Trihedron:
    """The orthogonal projection of a trihedron.

    It is basically a collection of marks defining the axonometric space.
    From the trihedron one can extract the tilted main reference planes.
    This class is creating the ReferencePlanes and holds geometric operations
    called in the parent Axonometry object.

    :param angles: Standard axonometric notation; left/right angles from 'horizon' for
      x/y coordinate axes.
    :param position: Center of the trihedron; (0,0) by default.
    :param size: The length of coordinate plane axes; 100 by default.
    :param ref_planes_distance: Reference plane translation distance from the trihedron
      center; 100 by default.
    """

    def __init__(
        self,
        angles: tuple[float, float],
        position: tuple[float, float] = (0, 0),
        size: float = 100.0,
        ref_planes_distance: float = 100.0,
    ) -> None:
        # Check if input is valid
        assert is_valid_angle_pair(angles), "Angle can not be 0. Approximate zero with .1"
        # Initialize object
        logger.debug(
            f"[{self}] Trihedron {position=}, {size=}, {ref_planes_distance=}",
        )
        self.axo = None  # set by parent
        self.axo_angles: tuple[float, float] = (
            math.radians(angles[0]),
            math.radians(angles[1]),
        )
        self.position: tuple[float, float] = position
        self.size: float = size
        self.axes: dict[Literal["x", "y", "z"], CLine] = self._setup_axes()
        self.reference_planes = self._setup_reference_planes(ref_planes_distance)

    def __repr__(self) -> str:
        """Trihedron."""
        return "Trihedron"

    # ==========================================================================
    # Methods
    # ==========================================================================

    def _setup_axes(self) -> dict[Literal["x", "y", "z"], CLine]:
        # parameters
        length = self.size
        alpha, beta = self.axo_angles
        # Calculate angles
        p0 = CPoint(*self.position)
        # Find second point by rotation and lenght
        p_x = self._rotated_point(p0, math.pi - alpha, length)
        p_y = self._rotated_point(p0, beta, length)
        # Always vertical
        p_z = CPoint(p0.x, p0.y - length)
        # Make axis lines
        axis_x, axis_y, axis_z = (
            CLine(p0, p_x),
            CLine(p0, p_y),
            CLine(p0, p_z),
        )

        return {"z": axis_z, "x": axis_x, "y": axis_y}

    def _setup_reference_planes(
        self,
        ref_planes_distance: float,
    ) -> dict[Literal["xy", "yz", "zx"], ReferencePlane]:
        axes_matrix_pairs = self._tilt_coordinate_planes(ref_planes_distance)

        ref_planes = {
            "xy": ReferencePlane(axes_matrix_pairs[0][0], self.axes["z"].direction),
            "yz": ReferencePlane(axes_matrix_pairs[1][0], self.axes["x"].direction),
            "zx": ReferencePlane(axes_matrix_pairs[2][0], self.axes["y"].direction),
        }

        ref_planes["xy"].matrix = axes_matrix_pairs[0][1]
        ref_planes["yz"].matrix = axes_matrix_pairs[1][1]
        ref_planes["zx"].matrix = axes_matrix_pairs[2][1]

        for key, plane in ref_planes.items():
            plane.key = key

        return ref_planes

    def _tilt_coordinate_planes(
        self,
        ref_planes_distance: float = 0.0,
    ) -> list[tuple[list[CLine], CTransformation]]:
        """Tilt the three reference planes (XY, ZY, and ZX).

        The function takes into account the distance to the reference planes and returns their
        geometric representations along with transformation matrices. N.B.: The code is not
        optimized for speed or repetitivity to make these operations as explicit as possibly.

        :param ref_planes_distance: The distance from the origin to each of the reference
          planes, defaults to .0.

        :return: A list containing tuples, where each tuple consists of a list of lines
          representing the axes of the tilted plane and a transformation matrix that can be
          applied to add geometric elements to the reference planes.
        """
        # Get the angles necessary to make the ReferencePlanes
        tilted_angle_pairs = self._get_tilted_angles()
        p0 = CPoint(*self.position)

        # XY
        angle_pair_xy = tilted_angle_pairs[0]
        # Translation by given distance and opposite axis
        TZ = CTranslation.from_vector(  # noqa: N806
            self.axes["z"].direction.inverted() * ref_planes_distance,
        )
        # Make axes lines
        p1 = self._rotated_point(p0, math.pi / 2 - angle_pair_xy[0], self.size)
        p2 = self._rotated_point(p0, math.pi / 2 + angle_pair_xy[1], self.size)
        XOY = [CLine(p0, p1).transformed(TZ), CLine(p0, p2).transformed(TZ)]  # noqa: N806
        # Compute Matrix
        vector_x = CVector.from_start_end(p0, p2)
        vector_y = CVector.from_start_end(p0, p1)
        F = CFrame(  # noqa: N806
            point=p0.transformed(TZ),
            xaxis=vector_x.transformed(TZ),
            yaxis=vector_y.transformed(TZ),
        )
        MZ = CTransformation.from_frame(F)  # noqa: N806

        # ZY
        angle_pair_zy = tilted_angle_pairs[1]
        # Translation by given distance and opposite axis
        TX = CTranslation.from_vector(  # noqa: N806
            self.axes["x"].direction.inverted() * ref_planes_distance,
        )
        # Make axes lines
        p1 = self._rotated_point(
            p0,
            (math.pi * 2 - self.axo_angles[0]) - angle_pair_zy[0],
            self.size,
        )
        p2 = self._rotated_point(
            p0,
            (math.pi * 2 - self.axo_angles[0]) + angle_pair_zy[1],
            self.size,
        )
        YOZ = [CLine(p0, p1).transformed(TX), CLine(p0, p2).transformed(TX)]  # noqa: N806
        # Compute Matrix
        axis_y = CVector.from_start_end(p0, p1)
        axis_z = CVector.from_start_end(p0, p2)
        F = CFrame(  # noqa: N806
            point=p0.transformed(TX),
            xaxis=axis_y.transformed(TX),
            yaxis=axis_z.transformed(TX),
        )
        MX = CTransformation.from_frame(F)  # noqa: N806

        # ZX
        angle_pair_zx = tilted_angle_pairs[2]
        # Translation by given distance and opposite axis
        TY = CTranslation.from_vector(  # noqa: N806
            self.axes["y"].direction.inverted() * ref_planes_distance,
        )
        # Make axes lines
        p1 = self._rotated_point(
            p0,
            (math.pi + self.axo_angles[1]) - angle_pair_zx[0],
            self.size,
        )
        p2 = self._rotated_point(
            p0,
            (math.pi + self.axo_angles[1]) + angle_pair_zx[1],
            self.size,
        )
        ZOX = [CLine(p0, p1).transformed(TY), CLine(p0, p2).transformed(TY)]  # noqa: N806
        # Compute Matrix
        axis_z = CVector.from_start_end(p0, p2)
        axis_x = CVector.from_start_end(p0, p1)
        F = CFrame(  # noqa: N806
            point=p0.transformed(TY),
            xaxis=axis_x.transformed(TY),
            yaxis=axis_z.transformed(TY),
        )
        # get frame matrix
        MY = CTransformation.from_frame(F)  # noqa: N806

        return [(XOY, MZ), (YOZ, MX), (ZOX, MY)]

    def _axis_angles(self) -> list[float]:
        """To be used to translate the reference planes."""
        zero = CVector.Xaxis()
        return [math.degrees(axis.direction.angle(zero)) for axis in self.axes.values()]

    def _get_tilted_angles(self) -> list[tuple[float]]:
        """Order by coordinate plane is XY, ZY, ZX."""
        a_z, a_x, a_y = (
            math.pi - (self.axo_angles[0] + self.axo_angles[1]),
            math.pi / 2 + self.axo_angles[1],
            math.pi / 2 + self.axo_angles[0],
        )
        assert math.isclose(
            a_z + a_x + a_y,
            math.pi * 2,
        ), (
            f"Something went wrong with the Axonometry angles: a_z = {int(math.degrees(a_z))}° / a_x = {int(math.degrees(a_x))}° / a_y = {int(math.degrees(a_y))}°"
        )
        logger.debug(
            f"[Trihedron] Compute tilt for axo system: a_z = {int(math.degrees(a_z))}° / a_x = {int(math.degrees(a_x))}° / a_y = {int(math.degrees(a_y))}°",
        )
        # progress counter-clockwise
        angle_pairs = [
            (a_y - math.pi / 2, a_x - math.pi / 2),
            (a_z - math.pi / 2, a_y - math.pi / 2),
            (a_x - math.pi / 2, a_z - math.pi / 2),
        ]
        # Get angles for each coordinate plane
        return [self._tilt(angle_pair) for angle_pair in angle_pairs]

    def _tilt(self, angles: tuple[float, float]) -> tuple[float, float]:
        """Coordinate plane tilt."""
        alpha = math.pi / 2 - angles[0]
        beta = math.pi / 2 - angles[1]

        OP = 1  # noqa: N806
        XP = abs(OP / math.tan(alpha))  # noqa: N806
        YP = abs(OP / math.tan(beta))  # noqa: N806

        h = math.sqrt(XP * YP)

        gamma = math.atan(XP / h)
        delta = math.atan(YP / h)

        assert math.isclose(gamma + delta, math.pi / 2)
        return (gamma, delta)

    def _rotated_point(self, p0: CPoint, angle: float, length: float) -> CPoint:
        # Calculate the new point after rotation
        x = p0.x + length * math.cos(angle)
        y = p0.y + length * math.sin(angle)
        return CPoint(x, y)


# ==========================================================================
# Utilities
# ==========================================================================


def random_valid_angles() -> tuple:
    """Compute an angle pair which can produce a valid axonometric drawing.

    The notation follows standard hand-drawn axonometry conventions expressed as a tuple of
    the two angles between the X and Y from the "axonoemtric horizon".

    TODO: allow a zero angle value.

    """
    import random

    alpha = random.choice(list(range(91)))  # noqa: S311
    beta = random.choice(list(range(91)))  # noqa: S311
    while not is_valid_angle_pair((alpha, beta)):
        alpha = random.choice(list(range(91)))  # noqa: S311
        beta = random.choice(list(range(91)))  # noqa: S311

    return (alpha, beta)


# ==========================================================================
# Predicates
# ==========================================================================


def is_valid_angle_pair(angles: tuple) -> bool:
    """Test if an angle pair are valid axonometry angles.

    Check if angles satisfy the following conditions::

        not (180 - (alpha + beta) >= 90 and
        not (alpha == 0 and beta == 0) and
        not (alpha == 90 and beta == 0) and
        not (alpha == 0 and beta == 90)

    .. hint::

        Currently the angle value 0 is not supported.
        But one can use a float vlue of .1 to approximate zero.
    """
    right_angle = 90
    return (
        180 - (angles[0] + angles[1]) >= right_angle
        and not (angles[0] == 0 and angles[1] == 0)
        and not (angles[0] == right_angle and angles[1] == 0)
        and not (angles[0] == 0 and angles[1] == right_angle)
    )
