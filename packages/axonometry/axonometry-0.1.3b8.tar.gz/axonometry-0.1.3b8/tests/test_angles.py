# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

import unittest

from axonometry import Axonometry, config_manager
from axonometry.trihedron import is_valid_angle_pair

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryAngles(unittest.TestCase):

    def test_angles(self):
        """Test creating Axonometry instances with series of angles."""
        for alpha in range(0, 91):
            for beta in range(0, 91):
                if is_valid_angle_pair((alpha, beta)):
                    """Test with valid angle pair."""
                    ax = Axonometry(alpha, beta)
                    self.assertIsNotNone(ax, f"Failed with alpha={alpha}, beta={beta}")
                else:
                    """Test with invalid angle pair."""
                    with self.assertRaises(
                        AssertionError,
                        msg=f"Accepted invalid angle pair (alpha={alpha}, beta={beta}",
                    ):
                        Axonometry(alpha, beta)


if __name__ == "__main__":
    unittest.main()
