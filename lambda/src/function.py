import json
import logging
import os
from datetime import datetime

import boto3
from pytz import timezone

# ========== Environment Variables to be configured ==========
TIMEZONE = os.getenv("TIMEZONE", "UTC")

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rds = boto3.client("rds")


def lambda_handler(event: dict, context: dict):
    logger.info(f"Input: {json.dumps(event)}")

    current_hour = str(datetime.now(tz=timezone(TIMEZONE)).hour)

    logger.info(f"current hour: {current_hour}")

    stop_rds_instances(current_hour)
    start_rds_instances(current_hour)

    stop_rds_clusters(current_hour)
    start_rds_clusters(current_hour)


def get_rds_instances_by_tag(name, value):
    instances = []
    res = rds.describe_db_instances()
    instances += res["DBInstances"]
    while "nextToken" in res:
        res = rds.describe_db_instances(nextToken=res["nextToken"])
        instances += res["DBInstances"]

    filtered = []
    for i in instances:
        if next((t for t in i["TagList"] if t["Key"] == name and t["Value"] == value), None):
            filtered.append(i)

    return filtered


def stop_rds_instances(current_hour: str):
    instances = get_rds_instances_by_tag("AutoStopTime", current_hour)
    instances_to_stop = [i for i in instances if i["DBInstanceStatus"] == "available"]

    if not instances_to_stop:
        logger.info("no instances to stop.")
        return

    logger.info(f"{len(instances_to_stop)} instances to stop.")
    for i in instances_to_stop:
        logger.info(f'identifier: {i["DBInstanceIdentifier"]}')

    for i in instances_to_stop:
        rds.stop_db_instance(DBInstanceIdentifier=i["DBInstanceIdentifier"])


def start_rds_instances(current_hour: str):
    instances = get_rds_instances_by_tag("AutoStartTime", current_hour)
    instances_to_start = [i for i in instances if i["DBInstanceStatus"] == "stopped"]

    if not instances_to_start:
        logger.info("no instances to start.")
        return

    logger.info(f"{len(instances_to_start)} instances to start.")
    for i in instances_to_start:
        logger.info(f'identifier: {i["DBInstanceIdentifier"]}')

    for i in instances_to_start:
        rds.start_db_instance(DBInstanceIdentifier=i["DBInstanceIdentifier"])


def get_rds_clusters_by_tag(name, value):
    clusters = []
    res = rds.describe_db_clusters()
    clusters += res["DBClusters"]
    while "nextToken" in res:
        res = rds.describe_db_instances(nextToken=res["nextToken"])
        clusters += res["DBClusters"]

    filtered = []
    for i in clusters:
        if next((t for t in i["TagList"] if t["Key"] == name and t["Value"] == value), None):
            filtered.append(i)

    return filtered


def stop_rds_clusters(current_hour: str):
    clusters = get_rds_clusters_by_tag("AutoStopTime", current_hour)
    clusters_to_stop = [i for i in clusters if i["Status"] == "available"]

    if not clusters_to_stop:
        logger.info(f"no clusters to stop.")
        return

    logger.info(f"{len(clusters_to_stop)} clusters to stop.")
    for i in clusters_to_stop:
        logger.info(f'identifier: {i["DBClusterIdentifier"]}')

    for i in clusters_to_stop:
        try:
            rds.stop_db_cluster(DBClusterIdentifier=i["DBClusterIdentifier"])
        except:
            logger.exception(f'failed to stop {i["DBClusterIdentifier"]}')


def start_rds_clusters(current_hour: str):
    clusters = get_rds_clusters_by_tag("AutoStartTime", current_hour)
    clusters_to_start = [i for i in clusters if i["Status"] == "stopped"]

    if not clusters_to_start:
        logger.info("no clusters to start.")
        return

    logger.info(f"{len(clusters_to_start)} clusters to start.")
    for i in clusters:
        logger.info(f'identifier: {i["DBClusterIdentifier"]}')

    for i in clusters_to_start:
        try:
            rds.start_db_cluster(DBClusterIdentifier=i["DBClusterIdentifier"])
        except:
            logger.exception(f'failed to start {i["DBClusterIdentifier"]}')
