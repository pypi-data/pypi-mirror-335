# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from math import dist
import unittest
from unittest.mock import patch
import random

from axonometry import Axonometry, Line, Point, config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryLines(unittest.TestCase):

    def setUp(self):
        self.axo = Axonometry.random_angles()
        # axo line projection propagation
        self.line_xyz_1 = self.axo.draw_line(Line.random_line())
        self.line_xyz_2 = self.axo.draw_line(Line.random_line())
        self.axo.draw_line(Line(self.line_xyz_1.end, self.line_xyz_2.start))
        # ref plane line projection propagation
        self.p_xy_1 = self.axo["xy"].draw_point(Point.random_point("xy"))
        self.p_xy_2 = self.axo["xy"].draw_point(Point.random_point("xy"))
        self.p_xy_1.project(distance=random.randint(50,100))
        self.p_xy_2.project(distance=random.randint(50,100))
        self.axo["xy"].draw_line(Line(self.p_xy_1, self.p_xy_2))

    def test_line_projections(self):
        pts = len(self.axo.points) + len(self.axo["xy"].points) + len(self.axo["yz"].points) + len(self.axo["zx"].points)
        self.assertEqual(pts, 22)
        lns = len(self.axo.lines) + len(self.axo["xy"].lines) + len(self.axo["yz"].lines) + len(self.axo["zx"].lines)
        self.assertTrue(9 <= lns <= 12)

    @patch("axonometry.Axonometry.save_svg")
    def test_saving_svg(self, mock_save_svg):
        svg_file = "test_axo_lines.svg"
        # Test saving an Axonometry instance to a SVG file.
        self.axo.save_svg(svg_file)
        mock_save_svg.assert_called_once_with(svg_file)

    @patch("axonometry.Axonometry.show_paths")
    def test_display_result(self, mock_show):
        self.axo.show_paths()
        mock_show.assert_called_once()

if __name__ == "__main__":
    unittest.main()
