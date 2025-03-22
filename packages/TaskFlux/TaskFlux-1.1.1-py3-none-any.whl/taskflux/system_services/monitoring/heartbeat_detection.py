# -*- encoding: utf-8 -*-

import time
import argparse

from taskflux.ameta.key import *
from taskflux.utils.parser import load_config
from taskflux.logger.logger import initialization_logger, logger
from taskflux.databases.mongo_api import initialization_mongo, node_insert_one

from taskflux.system_services.monitoring.system_info import NodeInfo


class HeartbeatDetection:
    """
    A class responsible for performing heartbeat detection.
    It continuously monitors the node's information and updates the database accordingly.
    """

    def __init__(self, config: dict):
        """
        Initialize the HeartbeatDetection instance.

        Args:
            config (dict): Configuration dictionary containing necessary settings.
        """

        initialization_logger(config=config)
        initialization_mongo(config=config)

        self.logger = logger(filename=KEY_PROJECT_NAME, task_id='HeartbeatDetection')

    def start(self):
        """
        Start the heartbeat detection process.
        This method runs in an infinite loop, periodically checking the node's information
        and updating the database. If an exception occurs, it logs the error and continues.
        """
        while True:
            try:

                node_info = NodeInfo()
                self.logger.info(f"{node_info.node}")
                node_insert_one(query={KEY_NODE_IPADDR: node_info.ipaddr}, data=node_info.node)

                time.sleep(60)
            except Exception as e:
                self.logger.error(f"[HeartbeatDetection] {e}")
                time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run heartbeat detection script")

    parser.add_argument("--config", type=str, help="heartbeat detection config")
    args = parser.parse_args()

    configs = load_config(args.config)

    HeartbeatDetection(configs).start()
