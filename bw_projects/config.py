"""Configurations for bw_projects."""
from pathlib import Path
from typing import Final, List

import platformdirs


class Configuration:
    """Configurations for bw_projects."""

    DIRS_BASIC: Final[List[str]] = [
        "backups",
        "intermediate",
        "lci",
        "processed",
    ]

    def __init__(
        self,
        app_name: str = "Brightway3",
        app_author: str = "pycla",
        dir_relative_logs: str = "logs",
        dirs_basic: List[str] = None,
        output_dir: Path = Path.home(),
    ) -> None:
        if dirs_basic is None:
            dirs_basic = self.DIRS_BASIC

        self.dir_base = Path(platformdirs.user_data_dir(app_name, app_author))
        self.dir_logs = Path(platformdirs.user_log_dir(app_name, app_author))
        self.dir_relative_logs = dir_relative_logs
        self.output_dir = output_dir
        self.dirs_basic = dirs_basic
