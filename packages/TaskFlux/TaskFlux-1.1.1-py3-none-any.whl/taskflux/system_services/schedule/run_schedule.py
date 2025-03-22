# -*- encoding: utf-8 -*-

import sys
import time
import argparse

from taskflux.ameta.key import *
from taskflux.queue.rabbitmq import initialization_rabbitmq
from taskflux.databases.mongo_api import initialization_mongo
from taskflux.interface.interface import databases_send_message
from taskflux.logger.logger import logger, initialization_logger
from taskflux.utils.parser import load_config, task_required_field_check


class RunSchedule:
    """
    Singleton class for managing the run schedule.
    """

    def __init__(self, config):
        """
        Initializes the RunSchedule instance.
        Args:
            config (dict): The configuration dictionary.
        """
        initialization_logger(config=config)
        initialization_rabbitmq(config=config)
        initialization_mongo(config=config)

        self.config = config
        self.system_default_schedule_time = config.get(KEY_DEFAULT_SCHEDULE_TIME, 10)
        self.logger = logger(filename=KEY_PROJECT_NAME, task_id='task_distribution')

    def task_distribution(self):
        """
        Distributes tasks based on the configuration.
        """
        message = {
            'self_config': self.config,
            KEY_TASK_ID: 'task_distribution',
            KEY_TASK_IS_SUB_TASK: False
        }
        message = task_required_field_check(message=message)
        queue_name = '{}_task_distribution'.format(KEY_SYSTEM_SERVICE_NAME)
        message['queue_name'] = queue_name

        databases_send_message(queue=queue_name, message=message)

    def run(self):
        while True:
            try:
                self.task_distribution()
                time.sleep(self.system_default_schedule_time)
            except Exception as e:
                self.logger.error('run schedule error: {}'.format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run schedule script")

    parser.add_argument("--config", type=str, help="run schedule config")
    args = parser.parse_args()

    configs = load_config(args.config)

    sys.path.append(configs[KEY_ROOT_PATH])

    RunSchedule(config=configs).run()
