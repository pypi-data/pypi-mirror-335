# -*- encoding: utf-8 -*-

import json
import uuid
import logging

from taskflux.ameta import *
from taskflux.main.main import *
from taskflux.cipher.rsa import *
from taskflux.utils.parser import *
from taskflux.logger.logger import *
from taskflux.utils.network import *
from taskflux.queue.rabbitmq import *
from taskflux.utils.timeformat import *
from taskflux.rpc_proxy.rpc_proxy import *
from taskflux.rpc_proxy.decorator import *
from taskflux.interface.interface import *
from taskflux.databases.mongo_api import *
from taskflux.generateId.snowflake import *


class TaskFlux:
    """
    TaskFlux is a singleton class designed to manage and schedule RPC services.
    It initializes various components such as logging, message queues, RPC proxies,
    and databases based on the provided configuration.

    Example usage:
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))

        config = {
            'MONGODB_CONFIG': 'mongodb://scheduleAdmin:scheduleAdminPasswrd@127.0.0.1:27017',
            'RABBITMQ_CONFIG': 'amqp://scheduleAdmin:scheduleAdminPasswrd@127.0.0.1:5672',
            'ROOT_PATH': current_dir,
            'ADMIN_USERNAME': 'scheduleAdmin',  # default is scheduleAdmin
            'ADMIN_PASSWORD': 'scheduleAdminPasswrd',  # default is scheduleAdminPasswrd
            'DEFAULT_SCHEDULE_TIME': 10,  # default is 10
            'HTTP_SERVER_FORK': False  # default is True
        }

        nf = TaskFlux(config=config)
    """

    def __init__(self, config: dict, is_cipher: bool = False):
        """
        Initializes the TaskFlux instance with the provided configuration.
        Args:
            config (dict): A dictionary containing the configuration settings.
            is_cipher (bool, optional): A flag indicating whether the configuration is encrypted. Defaults to False.
        Raises:
            Exception: If the configuration is invalid or missing required keys.
        """
        if KEY_ROOT_PATH not in config:
            raise Exception('Error ROOT_PATH not in config')

        if is_cipher:
            cipher_config = encrypt(plaintext=config[KEY_CIPHER_CIPHERTEXT], public_key=config[KEY_CIPHER_PUBLIC_KEY])
            config_dict = json.loads(cipher_config)
            config_dict[KEY_ROOT_PATH] = config[KEY_ROOT_PATH]
        else:
            config_dict = config

        initialization_global_attr(config_dict)

    @property
    def generate_id(self, module='snowflake_id') -> str:
        """
        Generate a unique ID using the Snowflake algorithm.
        Returns:
            str: The generated ID.
        """
        if module == 'snowflake_id':
            return snowflake_id()

        return str(uuid.uuid4())

    @property
    def ipaddr(self) -> str:
        """
        Get the IP address of the current machine.
        Returns:
            str: The IP address.
        """

        return get_ipaddr()

    @property
    def loguru(self, filename: str = None, task_id: str = None) -> logging:
        """
        Get a logger instance for logging.
        Args:
            filename (str): The name of the log file.
            task_id (str, optional): The ID of the task. Defaults to None.
        Returns:
            logging: The logger instance.
        """

        if task_id and filename:
            return logger(filename=filename, task_id=task_id)
        return logger(filename=KEY_PROJECT_NAME, task_id=KEY_PROJECT_NAME)

    @staticmethod
    def registry(services: list):
        """
        Register a list of services.

        Args:
            services (list): A list of service instances to be registered.

        This method registers each service in the provided list with the service management module.

        Each service is expected to have a 'register' method that is called to complete the registration process.
        """
        services_registry(services=services)

    @staticmethod
    def start():
        """
        Start the services.
        This method starts the services registered with the service management module.
        It calls the 'services_start' function to initiate the service startup process.
        """
        services_start()

    @staticmethod
    def proxy_call(service_name: str, method_name: str, **params):
        """
        Call a remote method on the specified service.
        Args:
            service_name (str): The name of the service to call.
            method_name (str): The name of the method to call on the service.
            **params: Additional parameters to pass to the method.
        Returns:
            The result of the remote method call.
        """

        return proxy_call(service_name, method_name, **params)

    @staticmethod
    def remote_call(service_name: str, method_name: str, **params):
        """
        Call a remote method on the specified service.
        Args:
            service_name (str): The name of the service to call.
            method_name (str): The name of the method to call on the service.
            **params: Additional parameters to pass to the method.
        Returns:
            The result of the remote method call.
        """

        return remote_call(service_name, method_name, **params)

    @staticmethod
    def stop_task(task_id: str):
        """
        Stop a task by the given task ID.
        Args:
            task_id (str): The unique identifier of the task.
        Returns:
            None
        """
        task_stop(task_id)

    @staticmethod
    def retry_task(task_id: str):
        """
        Stop a task by the given task ID.
        Args:
            task_id (str): The unique identifier of the task.
        Returns:
            None
        """
        task_retry(task_id)

    @staticmethod
    def query_service_list(query: dict, field: dict, limit: int, skip_no: int):
        """
        Query the list of services from the database.
        Args:
            query (dict): The query criteria.
            field (dict): The fields to include in the result.
            limit (int): The maximum number of results to return.
            skip_no (int): The number of results to skip.
        Returns:
            list: The list of services.
        """

        return query_service_list(query=query, field=field, limit=limit, skip_no=skip_no)

    @staticmethod
    def query_task_list(query: dict, field: dict, limit: int, skip_no: int):
        """
        Query the list of tasks from the database.
        Args:
            query (dict): The query criteria.
            field (dict): The fields to include in the result.
            limit (int): The maximum number of results to return.
            skip_no (int): The number of results to skip.
        Returns:
            list: The list of services.
        """
        return query_task_list(query=query, field=field, limit=limit, skip_no=skip_no)

    @staticmethod
    def query_node_list(query: dict, field: dict, limit: int, skip_no: int):
        """
        Query the list of nodes from the database.
        Args:
            query (dict): The query criteria.
            field (dict): The fields to include in the result.
            limit (int): The maximum number of results to return.
            skip_no (int): The number of results to skip.
        Returns:
            list: The list of services.
        """
        return query_node_list(query=query, field=field, limit=limit, skip_no=skip_no)

    @staticmethod
    def query_task_status_by_task_id(task_id: str):
        """
        Retrieve the task status by the given task ID.

        Args:
            task_id (str): The unique identifier of the task.

        Returns:
            dict: The first document containing the task status information.
        """
        return query_task_status_by_task_id(task_id)

    @staticmethod
    def update_work_max_process(worker_name: str, worker_ipaddr: str, worker_max_process: int):
        """
        Update the maximum number of processes for a worker identified by its name and IP address.

        Args:
            worker_name (str): The name of the worker.
            worker_ipaddr (str): The IP address of the worker.
            worker_max_process (int): The new maximum number of processes for the worker.

        Returns:
            None
        """
        update_work_max_process(worker_name, worker_ipaddr, worker_max_process)

    @staticmethod
    def rabbit_send_message(queue_name: str, message: dict):
        """
        Send a message to the RabbitMQ server.
        Args:
            queue_name (str): The name of the queue to send the message to.
            message (dict): The message to be sent.
        Returns:
            None
        """
        send_message(queue=queue_name, message=message)

    @staticmethod
    def rabbit_receive_message(queue_name: str, callback):
        """
        Receive a message from the RabbitMQ server.
        Args:
            queue_name (str): The name of the queue to receive the message from.
            callback: The callback function to process the received message.
        Returns:
            dict: The received message.
        """

        return receive_message(queue=queue_name, callback=callback)

    @staticmethod
    def send_message(queue_name: str, message: dict, weight: int = DEFAULT_VALUE_TASK_WEIGHT) -> str:
        """
        Send a message to the queue.
        Args:
            queue_name (str): The name of the queue to send the message to.
            message (dict): The message to be sent.
            weight (int): The weight of the message. Default is 1.
        Returns:
            str: The task ID associated with the message.
        This method sends the provided message to the specified queue using the RabbitMQ instance.
        """

        return databases_send_message(queue=queue_name, message=message, weight=weight)

    @staticmethod
    def submit_task(queue_name: str, message: dict, weight: int = DEFAULT_VALUE_TASK_WEIGHT) -> str:
        """
        Submit a task to the specified queue.
        Args:
            queue_name (str): The name of the queue to submit the task to.
            message (dict): The message to be submitted as a task.
            weight (int): The weight of the task. Default is 1.
        Returns:
            str: The task ID associated with the submitted task.
        This method submits the provided task to the specified queue using the RabbitMQ instance.
        """

        return databases_submit_task(queue=queue_name, message=message, weight=weight)

    @staticmethod
    def create_subtask(source_task_id: str, subtask_queue: str, subtasks: list) -> list:
        """
        Create subtasks for a given source task.
        Args:
            source_task_id (str): The ID of the source task.
            subtask_queue (str): The name of the queue for the subtasks.
            subtasks (list): A list of subtasks to be created.
        Returns:
            list: A list of subtask IDs.
        """
        return databases_create_subtask(
            source_task_id=source_task_id, subtask_queue=subtask_queue, subtasks=subtasks)
