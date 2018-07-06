#!/usr/bin/env python
'''
Desired state @crontab
0 2 * * * gce python2 gcp_snapshots.py -c <config_path> -v <volume_name> -s <snapshot_name> -i <saved_snapshots> -l <log_path>
'''

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from datetime import datetime
import logging
import argparse
import re

# ---------- helpers
def setup_logging(logging_fileHandler, logging_formatter):
    logger = logging.getLogger()

    handler = logging.FileHandler(logging_fileHandler)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter( logging_formatter )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def setup_argparse():
    req_status = True
    config_path = './gcp_secrets.py'
    log_path = '/var/log/gcp_snapshots/gcp_snapshots.log'
    parser = argparse.ArgumentParser(description='Creates a snapshot from a volume in GCP')

    parser.add_argument("-c", "--config", help="Config file path (default="+ config_path +")", required=False, type=str, default=config_path)
    parser.add_argument("-v", "--volume", help="Volume to snapshot [REQUIRED]", required=req_status, type=str)
    parser.add_argument("-s", "--snapshot", help="Snapshot name must be lowercase letters, numbers, and hyphens [REQUIRED]", required=req_status, type=str)
    parser.add_argument("-i", "--iterations", help="Number of copies of the same snapshot [REQUIRED]", required=req_status, type=int, default=7)
    parser.add_argument("-l", "--log", help="Log file path (default="+ log_path +")", required=False, type=str, default=log_path)
    args_me = parser.parse_args()

    # check correct pattern
    if not re.match(r'^[a-z]+[a-z\-\0-9]+$', args_me.snapshot):
        parser.print_help()
        import sys; sys.exit('\033[91mREMEMBER: Snapshot name must be lowercase letters, numbers, and hyphens.\033[0m')
    return args_me

def get_gce_driver():
    ComputeEngine = get_driver(Provider.GCE)
    return ComputeEngine(SERVICE_ACCOUNT, SERVICE_ACCOUNT_KEY, project=PROJECT)

def find_volume(volume_name):
    gce = get_gce_driver()
    volumes = gce.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item

def find_snapshots_from_volume(volume_name):
    gce = get_gce_driver()
    volumes = gce.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item.list_snapshots()

# ---------- CRUDL
def create_snapshot(volume_name, snapshot_name):
    gce = get_gce_driver()
    try:
        snapshot = gce.create_volume_snapshot(find_volume(volume_name), snapshot_name)
        log_me.info('Created snapshot: %s', snapshot)
        return snapshot
    except Exception as ec:
        log_me.error('Error creating snapshot: %s', ec)
        import sys; sys.exit(1)

def search_destroy(args_me):
    volume_snaphosts = find_snapshots_from_volume(args_me.volume)
    # delete unmatching snapshots from list
    for index, value in enumerate(volume_snaphosts):
        name = value.name.split('-')
        unit = "-".join(name[:-4])
        if unit != args_me.snapshot:
            volume_snaphosts.pop(index)
    if len(volume_snaphosts) > args_me.iterations:
        # sort list of snapshots
        volume_snaphosts.sort(key=lambda snaphost: snaphost.created,
                              reverse=False)
        # delete old snapshots from GCP
        to_delete = len(volume_snaphosts) - args_me.iterations
        for item in volume_snaphosts:
            try:
                item.destroy()
            except Exception as ec:
                log_me.error('Error deleting snapshot: %s', ec)
                import sys; sys.exit(1)
            log_me.info('Deleted snapshot: %s', item)
            to_delete -= 1
            if to_delete <= 0: break;


if __name__ == '__main__':
    args_me = setup_argparse()
    execfile(args_me.config)

    logging_formatter = '%(asctime)s - %(levelname)s - %(message)s'
    log_me = setup_logging(args_me.log, logging_formatter)
    log_me.info("Running with: config="+ args_me.config +", iterations="+
                str(args_me.iterations) +", log="+ args_me.log +
                ", snapshot="+ args_me.snapshot +", volume="+ args_me.volume)

    create_snapshot(args_me.volume, args_me.snapshot +"-"+ datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    search_destroy(args_me)
