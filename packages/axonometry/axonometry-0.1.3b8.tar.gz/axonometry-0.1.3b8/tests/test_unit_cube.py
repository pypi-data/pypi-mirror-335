# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import unittest

from axonometry import config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAxonometryAngles(unittest.TestCase):

    def test_manual_unit_cube(self):
        pass


if __name__ == "__main__":
    unittest.main()
