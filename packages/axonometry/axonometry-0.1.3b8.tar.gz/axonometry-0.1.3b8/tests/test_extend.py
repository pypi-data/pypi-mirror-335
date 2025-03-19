# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest

from axonometry import Axonometry, Drawing, config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAxonometryLayout(unittest.TestCase):

    def setUp(self):
        self.drawing = Drawing()

    def test_two_axo_drawing(self):
        axo1 = Axonometry.random_angles()
        axo2 = Axonometry.random_angles()
        self.drawing.add_axonometry(axo1)
        self.drawing.add_axonometry(axo2)
        # self.drawing.show()


if __name__ == "__main__":
    unittest.main()
