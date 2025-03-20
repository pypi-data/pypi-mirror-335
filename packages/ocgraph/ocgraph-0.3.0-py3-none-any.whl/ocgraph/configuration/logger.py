# SPDX-License-Identifier: GTDGmbH
# Copyright 2024 by GTD GmbH.
"""Class configuring the OCGraph logging."""

from __future__ import annotations

import logging

# fmt: off
preset_logging: dict[str, dict[str, bool | int]] = {
    "development": {
        "file_log": True,
        "file_level": logging.DEBUG,
        "console_log": True,
        "console_level": logging.DEBUG,
    },

    "module": {
        "file_log": False,
        "file_level": logging.ERROR,
        "console_log": False,
        "console_level": logging.ERROR,
    },

    "default": {
        "file_log": True,
        "file_level": logging.INFO,
        "console_log": True,
        "console_level": logging.INFO,
    },
}
# fmt: on


class OCGraphLogger(logging.Logger):
    """Logging mechanism for module."""

    def __init__(self, name: str, preset: str = "default", file: str = "") -> None:
        super().__init__(name)
        log_config = preset_logging.get(preset)
        if log_config:
            if log_config["file_log"]:
                logging_file = file + ".log"
                file_stream = logging.FileHandler(logging_file)
                file_stream.setLevel(log_config["file_level"])
                self.addHandler(file_stream)
            if log_config["console_log"]:
                console_stream = logging.StreamHandler()
                console_stream.setLevel(log_config["console_level"])
                self.addHandler(console_stream)
