from typing import Dict, List

from prometheus_client import Gauge, Metric

from disk_usage_exporter.disk_usage_exporter import set_metric
from disk_usage_exporter.const import METRIC_LABEL_NAME


class TestMetricSetting:
    def test_setting(self, empty_gauge_metric: Gauge, sample_metric: Metric):
        path = "/data"
        size = "15"
        metric = empty_gauge_metric
        set_metric(metric, METRIC_LABEL_NAME, path, size)

        assert metric.collect() == [sample_metric]


    def test_multiple_setting(
            self, empty_gauge_metric: Gauge, raw_values: List[Dict[str, str]], metric_with_multiple_labels: Metric
    ):
        metric = empty_gauge_metric
        for raw_value in raw_values:
            set_metric(metric, METRIC_LABEL_NAME, raw_value["path"], raw_value["size"])

        assert metric.collect() == [metric_with_multiple_labels]
