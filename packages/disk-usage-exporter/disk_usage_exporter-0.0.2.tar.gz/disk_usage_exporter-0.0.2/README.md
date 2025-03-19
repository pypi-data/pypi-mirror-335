# disk_usage_exporter
Exporter for disk usage metrics.

<details>
  <summary>Metrics example</summary>

  ```
  # HELP python_gc_objects_collected_total Objects collected during gc
  # TYPE python_gc_objects_collected_total counter
  python_gc_objects_collected_total{generation="0"} 187734.0
  python_gc_objects_collected_total{generation="1"} 74395.0
  python_gc_objects_collected_total{generation="2"} 6222.0
  # HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
  # TYPE python_gc_objects_uncollectable_total counter
  python_gc_objects_uncollectable_total{generation="0"} 0.0
  python_gc_objects_uncollectable_total{generation="1"} 0.0
  python_gc_objects_uncollectable_total{generation="2"} 0.0
  # HELP python_gc_collections_total Number of times this generation was collected
  # TYPE python_gc_collections_total counter
  python_gc_collections_total{generation="0"} 363.0
  python_gc_collections_total{generation="1"} 33.0
  python_gc_collections_total{generation="2"} 2.0
  # HELP python_info Python platform information
  # TYPE python_info gauge
  python_info{implementation="CPython",major="3",minor="9",patchlevel="21",version="3.9.21"} 1.0
  # HELP process_virtual_memory_bytes Virtual memory size in bytes.
  # TYPE process_virtual_memory_bytes gauge
  process_virtual_memory_bytes 5.58657536e+08
  # HELP process_resident_memory_bytes Resident memory size in bytes.
  # TYPE process_resident_memory_bytes gauge
  process_resident_memory_bytes 2.072576e+07
  # HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
  # TYPE process_start_time_seconds gauge
  process_start_time_seconds 1.73804800503e+09
  # HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
  # TYPE process_cpu_seconds_total counter
  process_cpu_seconds_total 7.79
  # HELP process_open_fds Number of open file descriptors.
  # TYPE process_open_fds gauge
  process_open_fds 8.0
  # HELP process_max_fds Maximum number of open file descriptors.
  # TYPE process_max_fds gauge
  process_max_fds 1024.0
  # HELP disk_usage_by_directories Directory size
  # TYPE disk_usage_by_directories gauge
  disk_usage_by_directories{path="/media"} 4.0
  disk_usage_by_directories{path="/tmp"} 78660.0
  disk_usage_by_directories{path="/var"} 6.9855712e+07
  disk_usage_by_directories{path="/sys"} 0.0
  disk_usage_by_directories{path="/etc"} 25232.0
  disk_usage_by_directories{path="/lost+found"} 16.0
  disk_usage_by_directories{path="/boot"} 274220.0
  disk_usage_by_directories{path="/lib64"} 0.0
  disk_usage_by_directories{path="/srv"} 4.0
  disk_usage_by_directories{path="/opt"} 35116.0
  disk_usage_by_directories{path="/sbin"} 0.0
  disk_usage_by_directories{path="/data"} 2.7009988e+07
  disk_usage_by_directories{path="/bin"} 0.0
  disk_usage_by_directories{path="/mnt"} 4.0
  disk_usage_by_directories{path="/run"} 1.3066156e+07
  disk_usage_by_directories{path="/afs"} 4.0
  disk_usage_by_directories{path="/lib"} 0.0
  disk_usage_by_directories{path="/dev"} 16.0
  disk_usage_by_directories{path="/proc"} 0.0
  disk_usage_by_directories{path="/usr"} 4.38558e+06
  disk_usage_by_directories{path="/home"} 5.203604e+06
  disk_usage_by_directories{path="/root"} 2324.0
  ```
</details>

## Installation
### From PyPI
```bash
sudo -H pip install disk_usage_exporter
```
### From source
1. Install `build` package
```bash
python -m pip install build
```
2. Build package
```bash
python -m build
```
3. Install package
```bash
VERSION=0.0.2
sudo -H pip install dist/disk_usage_exporter-$VERSION-py3-none-any.whl
```

## Usage
```
usage: disk_usage_exporter [-h] [--addr ADDR] [--port PORT] [--search-root SEARCH_ROOT] [-d] [-v]

options:
  -h, --help            show this help message and exit
  --addr ADDR           specify metrics host
  --port PORT           specify metrics port
  --search-root SEARCH_ROOT
                        specify the directory that will be used to search for subdirectories to analyze
  -d, --debug           enable debug logs
  -v, --version         show program's version number and exit
```

## Prometheus configuration
1. Add a new job to Prometheus configuration:
`/etc/prometheus/prometheus.yml`
```yml
...
scrape_configs:
  - job_name: "disk_usage_exporter"
    static_configs:
      - targets: ["localhost:8100"] 
```
2. Restart Prometheus:
```
PROMETHEUS_HOST=localhost
PROMETHEUS_PORT=9091
curl -XPOST $PROMETHEUS_HOST:$PROMETHEUS_PORT/-/reload
```

## Systemd unit
1. Create a file named `/etc/systemd/system/disk_usage_exporter.service` and include the following:
```ini
[Unit]
Description=disk_usage_exporter service

[Service]
ExecStart=disk_usage_exporter

[Install]
WantedBy=multi-user.target
```
2. Reload the service files to include a new service:
```
sudo systemctl daemon-reload
```
3. Start service:
```
sudo systemctl start disk_usage_exporter
```

## ToDo:
- [x] Rename `constants.py` to `const.py`
- [x] Add default host and port to `const.py`
- [x] Add `--host` option
- [x] Add `--host` description to `README.md`
- [ ] Add `--max-depth` option
- [ ] Make getting values asynchronous
- [x] Make project structure similar to other prometheus exporters
- [ ] Add informative logging messages
- [x] Add CI with linter
- [x] Add tests
- [x] Add name for python process
- [ ] Add badges with code coverage and tests passing
- [x] Add test that checks metrics after a few seconds after startup
- [ ] Add info about cmd args default values to README.md
