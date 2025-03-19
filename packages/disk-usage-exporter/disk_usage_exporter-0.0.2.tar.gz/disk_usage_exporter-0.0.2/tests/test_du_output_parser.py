import logging

import pytest

from disk_usage_exporter.disk_usage_exporter import parse_output


@pytest.mark.usefixtures("sample_logger")
class TestDuOutputParser:
    @staticmethod
    def test_empty_output(sample_logger: logging.Logger):
        raw_data = ""
        output = parse_output(raw_data, sample_logger)
        assert output["directory"] == "" and output["size"] == ""

    @staticmethod
    def test_full_output(du_output: str, sample_logger: logging.Logger):
        raw_data = du_output
        output = parse_output(raw_data, sample_logger)
        assert output["directory"] == "/data" and output["size"] == "12"
