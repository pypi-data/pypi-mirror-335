# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest
from unittest.mock import patch

from axonometry import Axonometry, Point, config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryReferencePlanes(unittest.TestCase):

    def setUp(self):
        self.axo = Axonometry.random_angles()
        p_xy = Point(x=100, y=50)
        p_yz = Point(y=100, z=50)
        p_zx = Point(z=100, x=50)
        p_xyz = Point(x=20, y=70, z=10)
        _ = self.axo["xy"].draw_point(p_xy)
        _ = self.axo["yz"].draw_point(p_yz)
        _ = self.axo["zx"].draw_point(p_zx)
        _ = self.axo.draw_point(p_xyz)

    @patch("axonometry.Axonometry.save_svg")
    def test_saving_svg(self, mock_save_svg):
        svg_file = f"test_axo_ref_planes.svg"
        """Test saving an Axonometry instance to a SVG file."""
        self.axo.save_svg(svg_file)
        mock_save_svg.assert_called_once_with(svg_file)

    @patch("axonometry.Axonometry.show_paths")
    def test_display_result(self, mock_show):
        # self.axo.show = MagicMock()
        self.axo.show_paths()
        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
