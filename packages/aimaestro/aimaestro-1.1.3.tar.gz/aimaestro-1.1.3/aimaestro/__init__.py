# -*- encoding: utf-8 -*-
from .taskflux import *

from .abc_global import *


class AiMaestro:

    def __init__(self, config_file: str):
        GlobalVar(config_file=config_file)

        initialization_taskflux(config=GlobalVar().taskflux_config)

    @staticmethod
    def registry_services():
        from aimaestro.workflows.web_automation import web_automation

        services_registry(services=[web_automation])

    @staticmethod
    def start_services():
        services_start()
