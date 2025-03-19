# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest
from unittest.mock import patch

from axonometry import Axonometry, config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometrySaving(unittest.TestCase):

    def setUp(self):
        self.axo = Axonometry.random_angles()

    @patch("axonometry.Axonometry.save_svg")
    def test_saving_svg(self, mock_save_svg):
        svg_file = f"test_axo_save.svg"
        """Test saving an Axonometry instance to a SVG file."""
        self.axo.save_svg(svg_file)
        mock_save_svg.assert_called_once_with(svg_file)


if __name__ == "__main__":
    unittest.main()
