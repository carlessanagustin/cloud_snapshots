# Cloud snapshot script

Python script to snapshot volumes in Google Cloud Platform (gcp) or Rackspace (rs)

## Requirements

* Install Python libraries: `pip install -r requirements.txt`

### Google Cloud Platform (gcp)

* Libcloud documentation: http://libcloud.readthedocs.io/en/latest/compute/drivers/gce.html#connecting-to-google-compute-engine
* Service account role: Compute Storage Admin = roles/compute.storageAdmin (https://goo.gl/dTdbVw)
* GCP config file format (default = ./gcp_secrets.py):

```python
SERVICE_ACCOUNT = 'XXXXX'
SERVICE_ACCOUNT_KEY = 'XXXXX'
PROJECT = 'XXXXX'
```

### Rackspace (rs)

* Libcloud documentation: http://libcloud.readthedocs.io/en/latest/compute/drivers/rackspace.html
* API key: My Profile & Settings > Security Settings > API key
* RS config file format (default = ./gcp_secrets.py):

```python
USERNAME = ""
API_KEY = ""
# Supported regions: dfw, ord, iad, lon, syd, hkg
REGION = ""
```

## Setup

* Run: `make install`
* Logs path: `/var/log/cloud_snapshots/cloud_snapshots.log`
* Logrotate enabled: `/etc/logrotate.d/cloud_snapshots`

## Usage

```shell
usage: cloud_snapshots.py [-h] [-c CONFIG] [-l LOG] -v VOLUME -s SNAPSHOT -i ITERATIONS [-p PROVIDER]

Creates a snapshot from a volume in Rackspace

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Config file path (default=./gcp_secrets.py)
  -l LOG, --log LOG     Log file path
                        (default=/var/log/cloud_snapshots/cloud_snapshots.log)
  -v VOLUME, --volume VOLUME
                        Volume to snapshot [REQUIRED]
  -s SNAPSHOT, --snapshot SNAPSHOT
                        Snapshot name must be lowercase letters, numbers, and
                        hyphens [REQUIRED]
  -i ITERATIONS, --iterations ITERATIONS
                        Number of copies of the same snapshot [REQUIRED]
  -p PROVIDER, --provider PROVIDER
                        Cloud provider: gcp | rs (default=gcp)
```

## Examples

* From virtualenv:

```shell
source pyenv/bin/activate

./cloud_snapshots.py \
  -v my-test-volume \
	-s my-test-volume \
	-i 5 \
	-p rs \
	-c ./keys/rs_secrets-myaccount.py

deactivate
```

* In crontab

```shell
WORKING_FOLDER=/opt/cloud_snapshots

0 1 * * *   <username>   $WORKING_FOLDER/cloud_snapshots.py -v <volume_name> -s <snapshot_name> -c <config_path> -p [gcp | rs] -i <saved_snapshots> -l <log_path>
```
