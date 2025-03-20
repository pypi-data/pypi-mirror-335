import requests
import json
import os
import logging

from openrouter_manager.adapter.prompt import Prompt
from openrouter_manager.adapter.variable import Variable
from openrouter_manager.adapter.llm_exception import LLMException


class AiAgent():
    logger = logging.getLogger(__name__)
    API_URL = 'https://openrouter.ai/api/v1/chat/completions'
    LLM_MODEL = "deepseek/deepseek-chat:free"
    _instance = None

    prompt = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiAgent, cls).__new__(cls)
            try:
                prompt_file = kwargs.get('prompt_file')
                cls._instance._initialize(prompt_file)
            except Exception as e:
                cls._instance = None
                raise e
        return cls._instance

    def _initialize(self, prompt_file: str = None):
        """ Initializes API settings and loads the prompt. """
        api_key = os.getenv('AIAGENT_API_KEY')
        print(f'api key {api_key}')
        if not api_key:
            raise ValueError("AIAGENT_API_KEY is missing in environment variables")

        if prompt_file is None:
            prompt_file = os.getenv('AIAGENT_PROMPT_FILE')
        if not prompt_file or not os.path.exists(prompt_file):
            raise ValueError(f"Prompt file not found: {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        self.prompt = Prompt(prompt_content)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "koralat.co",
            "X-Title": "Koral Advanced Technology"
        }

    def resolve(self, variables: dict) -> str:
        """ Replaces variables in the prompt and sends the request to the LLM. """
        self.prompt.clean()
        for key, value in variables.items():
            variable = Variable(key, value)
            self.prompt.set_variable(variable)

        data = json.dumps({
            "model": self.LLM_MODEL,
            "messages": [{"role": "user", "content": str(self.prompt)}]
        })

        try:
            response = requests.post(self.API_URL, data=data, headers=self.headers)
            response.raise_for_status()  # Throws an error for HTTP status codes 4xx/5xx
            return response.json().get(
                'choices', [{}])[0].get('message', {}).get('content', '')
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise LLMException('Error requesting to LLM')

    def set_prompt(self, prompt_file: str):
        if not os.path.exists(prompt_file):
            raise ValueError(f"Prompt file not found: {prompt_file}")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        self.prompt = Prompt(prompt_content)
