import subprocess
import time

import requests

from disk_usage_exporter.const import METRICS_HOST, METRICS_PORT


class TestHTTPServer:
    def test_prometheus_http_server(self):
        exporter_process = subprocess.Popen(["python", "-m", "disk_usage_exporter.disk_usage_exporter"])
        time.sleep(5)

        response = requests.get(f"http://{METRICS_HOST}:{METRICS_PORT}/metrics")
        assert response.status_code == 200

        exporter_process.kill()
