# -*- encoding: utf-8 -*-
import os
import yaml

__all__ = ['ROOT_PATH', 'GlobalVar']

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class GlobalVar:
    _instance = None

    global_config = {}
    taskflux_config = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalVar, cls).__new__(cls)
            cls._instance.__initialize(*args, **kwargs)
        return cls._instance

    def __initialize(self, config_file: str):
        self.config_file = config_file
        self._load_global_config()
        self._load_taskflux_config()

    def _load_global_config(self):
        with open(self.config_file, "r", encoding="utf-8") as f:
            self.global_config = yaml.safe_load(f)

    def _load_taskflux_config(self):
        self.taskflux_config = {
            'ROOT_PATH': ROOT_PATH,
            'RABBITMQ_CONFIG': 'amqp://{}:{}@{}:{}'.format(
                self.global_config['RabbitMQ']['username'],
                self.global_config['RabbitMQ']['password'],
                self.global_config['RabbitMQ']['host'],
                self.global_config['RabbitMQ']['port']
            ),
            'MONGODB_CONFIG': 'mongodb://{}:{}@{}:{}'.format(
                self.global_config['Database']['mongodb']['username'],
                self.global_config['Database']['mongodb']['password'],
                self.global_config['Database']['mongodb']['host'],
                self.global_config['Database']['mongodb']['port']
            )
        }
