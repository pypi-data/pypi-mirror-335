# -*- encoding: utf-8 -*-
from openai import OpenAI
from typing import Literal
from aimaestro.abc_global import *


class OpenAIModel:

    def __init__(self,
                 model: Literal['deepseek-chat', 'deepseek-reasoner'],
                 temperature: int = 1.0):
        self._model = model
        self._temperature = temperature

        self._client = None

        self._app_key = None
        self._base_url = None
        self._config_key = 'OpenAI'

        self._system_roles = [
            {'role': 'system', 'content': 'You are an expert in network security.'}
        ]
        self._global_config = GlobalVar().global_config

        self._get_config()
        self._get_client()

    def get_response(self, messages: list):
        """
        Get the response from the OpenAI model.
         param prompt:
        """
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            stream=False
        )
        print(response.choices[0].message.content)

    def _get_client(self):
        """
        Get the OpenAI client.
        :return:
        """
        if self._client is None:
            self._client = OpenAI(api_key=self._app_key, base_url=self._base_url)
        return self._client

    def _get_config(self):
        """
        Get the configuration for the OpenAI model.
        :return:
        """
        if self._model in ['deepseek-chat', 'deepseek-reasoner']:
            self._app_key = self._global_config.get(self._config_key)['deepseek'].get('api_key')
            self._base_url = self._global_config.get(self._config_key)['deepseek'].get('base_url')
        return None
