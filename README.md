# Google Cloud Platform snapshot script

Python script to snapshot volumes in GCP.

## Requirements

* Install Python libraries: `pip install -r requirements.txt`
* Service account key file: http://libcloud.readthedocs.io/en/latest/compute/drivers/gce.html#connecting-to-google-compute-engine
* Service account role: Compute Storage Admin = roles/compute.storageAdmin (https://goo.gl/dTdbVw)
* GCP config file format (default = ./gcp_secrets.py):

```python
SERVICE_ACCOUNT = 'XXXXX'
SERVICE_ACCOUNT_KEY = 'XXXXX'
PROJECT = 'XXXXX'
```

## Setup

* Run: `make install`
* Logs path: `/var/log/gcp_snapshots/gcp_snapshots.log`
* Logrotate enabled: `/etc/logrotate.d/gcp_snapshots`

## Usage

```shell
usage: gcp_snapshots.py [-h] [-c CONFIG] -v VOLUME -s SNAPSHOT -i ITERATIONS [-l LOG]

Creates a snapshot from a volume in GCP

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file path (default=./gcp_secrets.py)
  -v VOLUME, --volume VOLUME
                        Volume to snapshot [REQUIRED]
  -s SNAPSHOT, --snapshot SNAPSHOT
                        Snapshot name must be lowercase letters, numbers, and
                        hyphens [REQUIRED]
  -i ITERATIONS, --iterations ITERATIONS
                        Number of copies of the same snapshot [REQUIRED]
  -l LOG, --log LOG     Log file path
                        (default=/var/log/gcp_snapshots/gcp_snapshots.log)
```

## Usage (extended)

* crontab + virtualenv:

```shell
0 2 * * * <username> source ./pyenv/bin/activate && python gcp_snapshots.py -c <config_path> -v <volume_name> -s <snapshot_name> -i <saved_snapshots> -l <log_path>
```
