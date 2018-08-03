#!/usr/bin/env python3

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
    config_path = './gcp_secrets.py'
    log_path = '/var/log/cloud_snapshots/cloud_snapshots.log'
    req_status = True

    parser = argparse.ArgumentParser(description='Creates a snapshot from a volume in Rackspace')

    parser.add_argument("-c", "--config", help="Config file path (default="+ config_path +")", required=False, type=str, default=config_path)
    parser.add_argument("-l", "--log", help="Log file path (default="+ log_path +")", required=False, type=str, default=log_path)
    parser.add_argument("-v", "--volume", help="Volume to snapshot [REQUIRED]", required=req_status, type=str)
    parser.add_argument("-s", "--snapshot", help="Snapshot name must be lowercase letters, numbers, and hyphens [REQUIRED]", required=req_status, type=str)
    parser.add_argument("-i", "--iterations", help="Number of copies of the same snapshot [REQUIRED]", required=req_status, type=int, default=7)
    parser.add_argument("-p", "--provider", help="Cloud provider: gcp | rs (default=gcp)", required=False, type=str, default='gcp')

    args_me = parser.parse_args()

    # check correct pattern
    if not re.match(r'^[a-z]+[a-z\-\0-9]+$', args_me.snapshot):
        parser.print_help()
        import sys; sys.exit('\033[91mREMEMBER: Snapshot name must be lowercase letters, numbers, and hyphens.\033[0m')
    return args_me

def get_provider_driver(provider):
    if provider == 'rs':
        driver = get_driver(Provider.RACKSPACE)
        return driver(USERNAME, API_KEY, region=REGION)
    elif provider == 'gcp':
        driver = get_driver(Provider.GCE)
        return driver(SERVICE_ACCOUNT, SERVICE_ACCOUNT_KEY, project=PROJECT)
    else:
        print('Wrong provider format. Options: -p rs | gcp')
        log_me.error('Wrong provider format: %s', provider)
        import sys; sys.exit(1)

def find_volume(volume_name, provider_driver):
    volumes = provider_driver.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item

def find_volume_snapshot(volume, snapshot_name, provider_driver):
    snapshots = provider_driver.list_volume_snapshots(volume)
    for item in snapshots:
        if item.name == snapshot_name:
            return item

def find_snapshots_from_volume(volume_name, provider_driver):
    volumes = provider_driver.list_volumes()
    for item in volumes:
        if item.name == volume_name:
            return item.list_snapshots()

# TODO: UNFINISHED due to image schedule enabled in Rackspace
#def find_image(image_name, provider_driver):
#    #provider_driver = get_provider_driver(args_me.provider)
#    images = provider_driver.list_images()
#    for item in images:
#        if item.name == image_name:
#            return item
#def find_node(node_name, provider_driver):
#    #provider_driver = get_provider_driver(args_me.provider)
#    nodes = provider_driver.list_nodes()
#    for item in nodes:
#        if item.name == node_name:
#            return item

# ---------- main
def create_snapshot(args_me, provider_driver):
    #provider_driver = get_provider_driver(args_me.provider)
    snapshot_name = args_me.snapshot +"-"+ datetime.now().strftime("%Y-%m-%d-%H%M%S")
    try:
        snapshot = provider_driver.create_volume_snapshot(find_volume(args_me.volume, provider_driver), snapshot_name)
        # rackspace only
        if args_me.provider == 'rs':
            while 'available' != find_volume_snapshot(find_volume(args_me.volume, provider_driver), snapshot_name, provider_driver).state:
                time.sleep(10)
        log_me.info('Created snapshot: %s', snapshot)
        return snapshot
    except Exception as ec:
        log_me.error('Error creating snapshot: %s', ec)
        import sys; sys.exit(1)

def search_destroy(args_me, provider_driver):
    volume_snapshots = find_snapshots_from_volume(args_me.volume, provider_driver)
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
                # rackspace only
                if args_me.provider == 'rs':
                    while 'None' != str(find_volume_snapshot(find_volume(args_me.volume, provider_driver), args_me.snapshot, provider_driver)):
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

    provider_driver = get_provider_driver(args_me.provider)
    create_snapshot(args_me, provider_driver)
    search_destroy(args_me, provider_driver)
