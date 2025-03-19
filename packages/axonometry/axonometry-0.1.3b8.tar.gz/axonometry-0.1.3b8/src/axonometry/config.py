# SPDX-FileCopyrightText: 2022-2025 Julien Rippinger
# SPDX-FileCopyrightText: 2019-2022 Antoine Beyeler & Contributors
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
import os
import pathlib
from typing import TYPE_CHECKING, Any

import tomli

if TYPE_CHECKING:
    from collections.abc import Mapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    r"""Helper class to load axonometry's TOML configuration file.

    This class is typically used via its singleton instance ``config``::

        >>> from axonometry import config_manager
        >>> config_manager.config["layers"]["axo_system"]["id"]
        1

    By default, built-in configuration packaged with axonometry are loaded at startup.
    If a file exists at path ``~/.axonometry.toml``, it will be loaded as well.
    Additionaly files may be loaded using the :func:`load_config_file` method.

    The file holds default values to be accessed based on certain inputs::

        >>> from axonometry import Axonometry
        >>> my_axo = Axonometry(15, 30, paper_size="A3")
        INFO:axonometry.axonometry:[XYZ] 15°/30°
        >>> my_axo.drawing.dimensions
        (2245.0393701054, 3178.5826772031)  # sizes in css pixel.

    The configuration follows the line weights implement the DIN A norm, i.e. a
    :math:`\sqrt{2} ≈ 1.4` relationship of sizes. As such the lineweights
    in mm are:

    +------+------+------+------+------+------+------+------+------+------+
    | 0.10 | 0.13 | 0.18 | 0.25 | 0.35 | 0.50 | 0.70 | 1.00 | 1.40 | 2.00 |
    +------+------+------+------+------+------+------+------+------+------+

    This relationship allows linewidths to be scaled coherently based on paper sizes.
    For example, a 2 mm line width on an A0 page becomes a 1.4 mm line width on an A1 page.

    Further reading: `Why A4? The Mathematical Beauty of Paper Size <https://web.archive.org/web/20230814124712/https://scilogs.spektrum.de/hlf/why-a4-the-mathematical-beauty-of-paper-size/>`__.

    .. literalinclude:: ../../../src/axonometry/axo_config.toml
      :caption: Default configuration values in ``axo_config.toml``
      :language: toml
      :lines: 5-

    """

    def __init__(self) -> None:
        self._config: dict = {}

    # ==========================================================================
    # Methods
    # ==========================================================================

    def load_config_file(self, path: str) -> None:
        """Load a config file and add its content to the configuration database.

        :param path: path of the config file. The configuration file must be in TOML format.
        """

        def _update(d: dict, u: Mapping) -> dict:
            """Overwrite list member, UNLESS they are list of table, in which case they must extend the list."""
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = _update(d.get(k, {}), v)
                elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    if k in d:
                        d[k].extend(v)
                    else:
                        d[k] = v
                else:
                    d[k] = v
            return d

        logger.info("Loading config file at location:", path)
        with open(path, "rb") as fp:
            self._config = _update(self._config, tomli.load(fp))

    @property
    def config(self) -> dict[str, Any]:
        """Access default configuration by key."""
        return self._config


# ==========================================================================
# Utilities
# ==========================================================================

config_manager = ConfigManager()


def _init() -> None:
    pathlib.Path("output/").mkdir(parents=True, exist_ok=True)
    config_manager.load_config_file(str(pathlib.Path(__file__).parent / "axo_config.toml"))
    path = os.path.expanduser("~/.aconometry.toml")
    if os.path.exists(path):
        config_manager.load_config_file(str(path))


_init()
