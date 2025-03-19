import logging

from disk_usage_exporter.release import __version__


DEFAULT_LOG_LEVEL = logging.INFO
PROCESS_TITLE = "disk_usage_exporter"
METRICS_HOST = "127.0.0.1"
METRICS_PORT = "8100"
METRIC_NAME = "disk_usage_by_directories"
METRIC_DESCRIPTION = "Directory size"
METRIC_LABEL_NAME = "path"
MAX_DEPTH = 1
SEARCH_ROOT = "/"
VERSION = __version__
