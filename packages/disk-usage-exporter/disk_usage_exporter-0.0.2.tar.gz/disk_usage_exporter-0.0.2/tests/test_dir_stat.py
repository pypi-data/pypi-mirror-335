from typing import Dict, List
import logging

from disk_usage_exporter.disk_usage_exporter import get_dir_stat


class TestDirStat:
    def test_dir_size(self, sample_directory_structure_with_data: List[Dict[str, str]], sample_logger: logging.Logger):
        dirs = sample_directory_structure_with_data

        for dir_values in dirs:
            name, size = get_dir_stat(dir_values["directory"], sample_logger)
            assert dir_values["directory"] == name and dir_values["size"] == size
