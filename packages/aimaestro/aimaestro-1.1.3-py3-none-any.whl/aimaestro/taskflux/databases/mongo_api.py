# -*- encoding: utf-8 -*-

from aimaestro.taskflux.ameta.key import *
from aimaestro.taskflux.databases.mongo_client import MongoClient

__all__ = [
    'initialization_mongo',
    'query_node_list',
    'node_insert_one',
    'query_service_list',
    'service_insert_one',
    'update_work_max_process',
    'query_task_list',
    'task_insert_one',
    'query_task_status_by_task_id',
    'task_stop',
    'task_retry',
    'query_run_task',
    'query_worker_running_number',
    'worker_push_process',
    'worker_pull_process'
]

_MONGODB_CONFIG = DEFAULT_VALUE_MONGODB_URI


class TaskAPI(MongoClient):
    """
        DatabaseTasks class is used to manage database task - related operations.
    """
    _table_name = TABLE_NAME_TASKS


class NodeAPI(MongoClient):
    """
        DatabaseNodes class is used to manage database nodes.
    """

    _table_name = TABLE_NAME_NODES


class ServiceAPI(MongoClient):
    """
        DatabaseServices class is used to manage database services - related operations.
    """
    _table_name = TABLE_NAME_SERVICES


def initialization_mongo(config: dict):
    """
    Initialize the logger with the given configuration.
    Args:
        config (dict): A dictionary containing the configuration.
    """
    global _MONGODB_CONFIG
    _MONGODB_CONFIG = config.get(KEY_MONGO_CONFIG)


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
    _database_nodes = NodeAPI(_MONGODB_CONFIG)
    return _database_nodes.query_list_sort(query=query, field=field, limit=limit, skip_no=skip_no)


def node_insert_one(query: dict, data: dict):
    """
    Insert a single document into the collection.

    Args:
        data (dict): A dictionary containing the data to insert.
        query (dict): A dictionary specifying the query criteria.
    """
    _database_nodes = NodeAPI(_MONGODB_CONFIG)
    _database_nodes.update_many(query=query, update_data=data, upsert=True)


############################################################################################
# ==================================== database_service ====================================
############################################################################################
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
    _database_services = ServiceAPI(_MONGODB_CONFIG)

    return _database_services.query_list_sort(query=query, field=field, limit=limit, skip_no=skip_no)


def service_insert_one(query: dict, data: dict):
    """
    Insert a single document into the collection.

    Args:
        data (dict): A dictionary containing the data to insert.
        query (dict): A dictionary specifying the query criteria.
    """
    _database_services = ServiceAPI(_MONGODB_CONFIG)
    _database_services.update_many(query=query, update_data=data, upsert=True)


def query_worker_running_number(query: dict):
    """
    Query the number of running workers based on the given query.
    Args:
        query (dict): A dictionary containing the query criteria.
    Returns:
        tuple: A tuple containing the number of running workers and the maximum number of workers.
    """
    _database_services = ServiceAPI(_MONGODB_CONFIG)
    data = _database_services.query_all(
        query=query,
        field={'_id': 0, KEY_WORKER_RUN_PROCESS: 1, KEY_WORKER_MAX_PROCESS: 1}
    )
    return len(data[0].get(KEY_WORKER_RUN_PROCESS)), data[0].get(KEY_WORKER_MAX_PROCESS)


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
    _database_services = ServiceAPI(_MONGODB_CONFIG)
    _database_services.update_many(
        query={
            KEY_WORKER_NAME: worker_name,
            KEY_WORKER_IPADDR: worker_ipaddr
        },
        update_data={
            KEY_WORKER_MAX_PROCESS: worker_max_process
        }
    )


def worker_push_process(worker_name: str, worker_ipaddr: str, worker_pid: int):
    """
    Update the maximum number of processes for a worker identified by its name and IP address.
    Args:
        worker_name (str): The name of the worker.
        worker_ipaddr (str): The IP address of the worker.
        worker_pid (int): The new maximum number of processes for the worker.
    Returns:
        None
    """
    _database_services = ServiceAPI(_MONGODB_CONFIG)
    _database_services.push_one(
        query={
            KEY_WORKER_NAME: worker_name,
            KEY_WORKER_IPADDR: worker_ipaddr
        },
        update_data={
            KEY_WORKER_RUN_PROCESS: worker_pid
        }
    )


def worker_pull_process(worker_name: str, worker_ipaddr: str, worker_pid: int):
    """
    Update the maximum number of processes for a worker identified by its name and IP address.
    Args:
        worker_name (str): The name of the worker.
        worker_ipaddr (str): The IP address of the worker.
        worker_pid (int): The new maximum number of processes for the worker.
    Returns:
        None
    """

    _database_services = ServiceAPI(_MONGODB_CONFIG)
    _database_services.pull_one(
        query={
            KEY_WORKER_NAME: worker_name,
            KEY_WORKER_IPADDR: worker_ipaddr
        },
        update_data={
            KEY_WORKER_RUN_PROCESS: worker_pid
        }
    )


############################################################################################
# ==================================== database_tasks ====================================
############################################################################################
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
    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    return _database_tasks.query_list_sort(query=query, field=field, limit=limit, skip_no=skip_no)


def task_insert_one(query: dict, data: dict):
    """
    Insert a single document into the collection.

    Args:
        data (dict): A dictionary containing the data to insert.
        query (dict): A dictionary specifying the query criteria.
    """
    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    _database_tasks.update_many(query=query, update_data=data, upsert=True)


def query_task_status_by_task_id(task_id: str):
    """
    Retrieve the task status by the given task ID.

    Args:
        task_id (str): The unique identifier of the task.

    Returns:
        dict: The first document containing the task status information.
    """
    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    data = _database_tasks.query_all(
        query={KEY_TASK_ID: task_id},
        field={
            '_id': 0, KEY_TASK_STATUS: 1,
            '{}.{}'.format(KEY_TASK_BODY, KEY_TASK_IS_SUB_TASK_ALL_FINISH): 1
        }
    )
    data = [i for i in data]
    return data[0]


def task_stop(task_id: str):
    """
    Stop a task by the given task ID.
    Args:
        task_id (str): The unique identifier of the task.
    Returns:
        None
    """
    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    _database_tasks.update_many(
        query={KEY_TASK_ID: task_id}, update_data={KEY_TASK_STATUS: KEY_TASK_STOP_STATUS})


def task_retry(task_id: str):
    """
    Stop a task by the given task ID.
    Args:
        task_id (str): The unique identifier of the task.
    Returns:
        None
    """

    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    _database_tasks.update_many(
        query={KEY_TASK_ID: task_id}, update_data={KEY_TASK_STATUS: KEY_TASK_WAIT_STATUS})


def query_run_task(query: dict):
    """
    Retrieve a list of tasks from the collection based on the given query, sorted by task weight.

    Args:
        query (dict): A dictionary representing the query conditions for filtering the tasks.

    Returns:
        list: A list of tasks that match the specified query, sorted by task weight in descending order.
    """
    _database_tasks = TaskAPI(_MONGODB_CONFIG)
    return _database_tasks.query_list_sort(
        query=query, field={'_id': 0}, limit=1000, skip_no=0, sort_field=KEY_TASK_WEIGHT)
