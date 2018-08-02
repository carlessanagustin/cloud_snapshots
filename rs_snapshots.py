#!/usr/bin/env python3
'''
Desired state @crontab
0 2 * * * gce python3 gcp_snapshots.py -c <config_path> -v <volume_name> -s <snapshot_name> -i <saved_snapshots> -l <log_path>
'''

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from datetime import datetime
import logging
import argparse
import re
import time

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
    req_status = False
    config_path = './rs_secrets.py'
    log_path = '/var/log/gcp_snapshots/rs_snapshots.log'
    parser = argparse.ArgumentParser(description='Creates a snapshot from a volume in Rackspace')

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

def get_rs_driver():
    driver = get_driver(Provider.RACKSPACE)
    return driver(USERNAME, API_KEY, region=REGION)

def find_volume(volume_name):
    gce = get_rs_driver()
    volumes = gce.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item

def find_volume_snapshot(volume, snapshot_name):
    gce = get_rs_driver()
    snapshots = gce.list_volume_snapshots(volume)
    for item in snapshots:
        if item.name == snapshot_name:
            return item

def find_image(image_name):
    gce = get_rs_driver()
    images = gce.list_images()
    for item in images:
        if item.name == image_name:
            return item

def find_node(node_name):
    gce = get_rs_driver()
    nodes = gce.list_nodes()
    for item in nodes:
        if item.name == node_name:
            return item

def find_snapshots_from_volume(volume_name):
    gce = get_rs_driver()
    volumes = gce.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item.list_snapshots()

# ---------- CRUDL
def create_snapshot(volume_name, snapshot_name):
    gce = get_rs_driver()
    try:
        snapshot = gce.create_volume_snapshot(find_volume(volume_name), snapshot_name)
        while 'available' != find_volume_snapshot(find_volume(volume_name), snapshot_name).state:
            time.sleep(10)

        log_me.info('Created snapshot: %s', snapshot)
        return snapshot
    except Exception as ec:
        log_me.error('Error creating snapshot: %s', ec)
        import sys; sys.exit(1)

def search_destroy(args_me):
    volume_snapshots = find_snapshots_from_volume(args_me.volume)
    # delete unmatching snapshots from list
    for index, value in enumerate(volume_snapshots):
        name = value.name.split('-')
        unit = "-".join(name[:-4])
        if unit != args_me.snapshot:
            volume_snapshots.pop(index)
    if len(volume_snapshots) > args_me.iterations:
        # sort list of snapshots
        volume_snapshots.sort(key=lambda snaphost: snaphost.created,
                              reverse=False)
        # delete old snapshots from GCP
        to_delete = len(volume_snapshots) - args_me.iterations
        for item in volume_snapshots:
            try:
                item.destroy()
                #while 'None' != item.state:
                while 'None' != str(find_volume_snapshot(find_volume(args_me.volume), args_me.snapshot)):
                    time.sleep(10)
                log_me.info('Deleted snapshot: %s', item)

            except Exception as ec:
                log_me.error('Error deleting snapshot: %s', ec)
                import sys; sys.exit(1)
            to_delete -= 1
            if to_delete <= 0: break;


if __name__ == '__main__':
    args_me = setup_argparse()
    exec(open(args_me.config).read())

    logging_formatter = '%(asctime)s - %(levelname)s - %(message)s'
    log_me = setup_logging(args_me.log, logging_formatter)
    log_me.info("Running with: config="+ args_me.config +", iterations="+
                str(args_me.iterations) +", log="+ args_me.log +
                ", snapshot="+ args_me.snapshot +", volume="+ args_me.volume)

    create_snapshot(args_me.volume, args_me.snapshot +"-"+ datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    search_destroy(args_me)
