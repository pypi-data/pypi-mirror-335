# -*- encoding: utf-8 -*-
import os
import sys
import argparse

from taskflux.ameta.key import *
from taskflux.ameta.abcmeta import ServiceConstructor

from taskflux.utils.parser import load_config
from taskflux.databases.mongo_api import service_insert_one
from taskflux.rpc_proxy.decorator import service_running
from taskflux.main.build import Build


class RunServer:

    def __init__(self, config, cls_path):
        self.config = config
        self.cls_path = cls_path

    def server_start(self):
        build = Build(
            config=self.config,
            cls_path=self.cls_path,
            build_type='service',
            constructor=ServiceConstructor
        )
        constructor = build.build(task_id=None)

        service_data = {
            KEY_NAME: constructor.name,
            KEY_SERVICE_IPADDR: constructor.service_ipaddr,
            KEY_SERVICE_NAME: constructor.service_name,
            KEY_SERVICE_VERSION: constructor.service_version,
            KEY_SERVICE_PID: os.getpid(),
            KEY_SERVICE_FUNCTIONS: constructor.functions
        }

        service_insert_one(
            query={
                KEY_SERVICE_IPADDR: constructor.service_ipaddr,
                KEY_SERVICE_NAME: constructor.service_name
            },
            data=service_data
        )
        constructor.logger.info('Service started == {}'.format(service_data))

        service_running(
            service_cls=constructor,
            config={KEY_RABBITMQ_URI: self.config.get(KEY_RABBITMQ_CONFIG)}
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="run service script")

    parser.add_argument("--config", type=str, help="service config")
    parser.add_argument("--path", type=str, help="service path")
    args = parser.parse_args()

    configs = load_config(args.config)

    sys.path.append(configs[KEY_ROOT_PATH])

    RunServer(config=configs, cls_path=args.path).server_start()
