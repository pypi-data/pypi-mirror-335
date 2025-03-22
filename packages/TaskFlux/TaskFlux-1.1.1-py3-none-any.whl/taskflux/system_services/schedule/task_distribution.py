# -*- encoding: utf-8 -*-

from taskflux.ameta.key import *
from taskflux.ameta.abcmeta import ServiceConstructor, WorkerConstructor
from taskflux.generateId.snowflake import snowflake_id

from taskflux.queue.rabbitmq import send_message
from taskflux.databases.mongo_api import query_run_task, query_service_list, task_insert_one
from taskflux.rpc_proxy.decorator import rpc


class RpcFunction(ServiceConstructor):
    """
    Class Name Not modifiable, Define RPC functions
    """
    service_name = '{}_task_distribution'.format(KEY_SYSTEM_SERVICE_NAME)

    def get_service_name(self, version):
        self.logger.info(f'version == {version}')
        return {"service_name": self.service_name, "version": version}

    @rpc
    def generate_id(self):
        return snowflake_id()


class WorkerFunction(WorkerConstructor):
    """
    Class Name Not modifiable, Worker Code for Task Distribution.

    This class is responsible for the task distribution logic within the system.
    It interacts with RabbitMQ and databases to manage tasks, filter them based on status,
    and distribute them to appropriate workers according to the worker's idle capacity.
    """

    worker_name = '{}_task_distribution'.format(KEY_SYSTEM_SERVICE_NAME)

    def run(self, data):
        """
            Execute the task distribution process.

            This method is the main entry point for the task distribution process.
            It retrieves the configuration from the input data, initializes connections to RabbitMQ and databases,
            fetches tasks from the database, processes them, and distributes them to workers.

            Args:
                data (dict): A dictionary containing the configuration and other relevant data.
                    It should have a key 'self_config' that holds the configuration.
        """
        system_services = [
            '{}_task_distribution'.format(KEY_SYSTEM_SERVICE_NAME)
        ]

        _, source_tasks = query_run_task(
            query={
                KEY_TASK_STATUS: {
                    '$in': [KEY_TASK_WAIT_STATUS, KEY_TASK_RUN_STATUS, KEY_TASK_SUCCESS_STATUS]
                },
                KEY_TASK_QUEUE_NAME: {'$nin': system_services}
            }
        )

        all_tasks = {}
        source_task_status = {}
        for task in source_tasks:
            task_id = task[KEY_TASK_ID]
            task_status = task[KEY_TASK_STATUS]
            queue_name = task[KEY_TASK_QUEUE_NAME]
            is_subtask = task[KEY_TASK_IS_SUB_TASK]

            if queue_name not in all_tasks:
                all_tasks[queue_name] = {
                    KEY_TASK_RUN_STATUS: {}, KEY_TASK_WAIT_STATUS: {}, KEY_TASK_SUCCESS_STATUS: {}}

            if is_subtask is False:
                source_task_status.setdefault(task_id, {'task_status': task_status, 'source_queue_name': queue_name})
                all_tasks[queue_name][task_status][task_id] = {'body': task, 'sub_tasks': []}

        for task in source_tasks:
            task_status = task[KEY_TASK_STATUS]
            queue_name = task[KEY_TASK_QUEUE_NAME]
            is_subtask = task[KEY_TASK_IS_SUB_TASK]
            source_id = task.get(KEY_TASK_SOURCE_ID)

            if task_status != KEY_TASK_WAIT_STATUS:
                continue

            if is_subtask:
                source_status = source_task_status[source_id]['task_status']
                source_queue_name = source_task_status[source_id]['source_queue_name']
                if source_status not in [KEY_TASK_STOP_STATUS, KEY_TASK_ERROR_STATUS]:
                    all_tasks[source_queue_name][source_status][source_id]['sub_tasks'].append(
                        {'body': task, 'queue_name': queue_name})

        run_tasks = {}
        sub_task_all_finish = {}
        for queue_name in all_tasks:
            if queue_name not in run_tasks:
                run_tasks[queue_name] = []

            for task_status in [KEY_TASK_RUN_STATUS, KEY_TASK_WAIT_STATUS, KEY_TASK_SUCCESS_STATUS]:
                for source_id in all_tasks[queue_name][task_status]:
                    task = all_tasks[queue_name][task_status][source_id]
                    sub_tasks = all_tasks[queue_name][task_status][source_id]['sub_tasks']

                    if task_status == KEY_TASK_WAIT_STATUS:
                        run_tasks[queue_name].append(task['body'])
                    else:
                        if len(sub_tasks) > 0:
                            for sub in sub_tasks:
                                sub_task = sub['body']
                                sub_task_queue_name = sub['queue_name']
                                if sub_task_queue_name not in run_tasks:
                                    run_tasks[sub_task_queue_name] = []

                                run_tasks[sub_task_queue_name].append(sub_task)
                        else:
                            sub_task_all_finish.setdefault(source_id, True)

        _, services = query_service_list(
            query={KEY_WORKER_NAME: {'$in': [i for i in run_tasks]}},
            field={'_id': 0, KEY_WORKER_NAME: 1, KEY_WORKER_MAX_PROCESS: 1, KEY_WORKER_RUN_PROCESS: 1},
            limit=10000, skip_no=0
        )

        worker_idle_number = {}
        for service in services:
            worker_name = service[KEY_WORKER_NAME]
            worker_max_process = service[KEY_WORKER_MAX_PROCESS]
            worker_run_process = len(service[KEY_WORKER_RUN_PROCESS])

            if worker_name not in worker_idle_number:
                worker_idle_number[worker_name] = 0
            worker_idle_number[worker_name] += worker_max_process - worker_run_process

        for queue_name in run_tasks:
            for task in run_tasks[queue_name]:
                if worker_idle_number[queue_name] > 0:
                    send_message(queue=queue_name, message=task[KEY_TASK_BODY])
                    self.logger.info(f'run task === {task[KEY_TASK_BODY]}')
                    worker_idle_number[queue_name] -= 1

        if len(sub_task_all_finish) > 0:
            task_insert_one(
                query={KEY_TASK_ID: {'$in': [i for i in sub_task_all_finish]}},
                data={KEY_TASK_IS_SUB_TASK_ALL_FINISH: True}
            )
