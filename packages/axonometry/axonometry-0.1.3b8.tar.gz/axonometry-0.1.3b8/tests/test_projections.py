# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest
from unittest.mock import patch

from axonometry import Axonometry, Line, Point, config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryProjections(unittest.TestCase):

    def setUp(self):
        self.axo = Axonometry.random_angles()

        # Creates a XYZ point by 2 random computed auxilary projections
        self.p0 = self.axo.draw_point(Point(x=15, y=15, z=30))
        # Project XYZ point on refernce planes. Existin points will not be created twice.
        _ = self.p0.project(ref_plane_key="xy")
        _ = self.p0.project(ref_plane_key="yz")
        _ = self.p0.project(ref_plane_key="zx")

        # Create point in XY reference plane
        self.p1 = self.axo["xy"].draw_point(Point(x=30, y=20))
        # Project point into XYZ
        self.p1_axo = self.p1.project(distance=50, auxilaray_plane_key="zx")
        # # Project on remaining reference planes
        self.p1_axo.project(ref_plane_key="yz", auxilaray_plane_key="zx")
        self.p1_axo.project(ref_plane_key="zx")

        self.p2 = self.axo["yz"].draw_point(Point(y=1, z=15))
        self.p2_axo = self.p2.project(distance=25)
        self.p2_axo.project(ref_plane_key="xy")
        self.p2_axo.project(ref_plane_key="zx")

        self.p3 = self.axo["zx"].draw_point(Point(z=5, x=10))
        self.p3_axo = self.p3.project(distance=15)
        self.p3_axo.project(ref_plane_key="xy")
        self.p3_axo.project(ref_plane_key="yz")

    def test_p0(self):
        self.assertEqual(len(self.p0.projections['xyz']), 0)
        self.assertEqual(self.p0.projections['xy'], self.p0)
        self.assertEqual(self.p0.projections['yz'], self.p0)
        self.assertEqual(self.p0.projections['zx'], self.p0)
        self.assertEqual(len([value for value in self.p0.projections.values() if isinstance(value, Point)]), 3)

    def test_p1_p2_p3(self):
        self.assertEqual(self.p1.projections['xyz'][0], self.p1_axo)
        self.assertEqual(len([value for value in self.p1_axo.projections.values() if isinstance(value, Point)]), 3)
        self.assertEqual(self.p2.projections['xyz'][0], self.p2_axo)
        self.assertEqual(len([value for value in self.p2_axo.projections.values() if isinstance(value, Point)]), 3)
        self.assertEqual(self.p3.projections['xyz'][0], self.p3_axo)
        self.assertEqual(len([value for value in self.p3_axo.projections.values() if isinstance(value, Point)]), 3)

    def test_plane_collections(self):
        self.assertEqual(len(self.axo.lines+self.axo.points), 4)
        self.assertEqual(len(self.axo['xy'].lines+self.axo['xy'].points), 4)
        self.assertEqual(len(self.axo['yz'].lines+self.axo['yz'].points), 4)
        self.assertEqual(len(self.axo['zx'].lines+self.axo['zx'].points), 4)

    @patch("axonometry.Axonometry.save_svg")
    def test_saving_svg(self, mock_save_svg):
        svg_file = f"test_axo_projections.svg"
        """Test saving an Axonometry instance to a SVG file."""
        self.axo.save_svg(svg_file)
        mock_save_svg.assert_called_once_with(svg_file)

    @patch("axonometry.Axonometry.show_paths")
    def test_display_result(self, mock_show):
        self.axo.show_paths()
        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
