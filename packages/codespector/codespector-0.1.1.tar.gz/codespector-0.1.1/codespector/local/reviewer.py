import os.path
from dataclasses import dataclass

import ujson
import requests

from loguru import logger

AGENT_URL_MAPPING = {
    'codestral': 'https://api.mistral.ai/v1/chat/completions',
    'chatgpt': 'https://api.openai.com/v1/chat/completions',
}

DEFAULT_AGENT_MODEL = {'codestral': 'codestral-latest', 'chatgpt': 'gpt-4o'}


@dataclass
class AgentInfo:
    model: str
    url: str
    headers: dict

    @classmethod
    def create(cls, chat_agent: str, chat_token: str, chat_model: str | None = None) -> 'AgentInfo':
        url = AGENT_URL_MAPPING[chat_agent]
        model = chat_model if chat_model else DEFAULT_AGENT_MODEL[chat_agent]
        headers = {'Authorization': f'Bearer {chat_token}'}
        return cls(
            url=url,
            model=model,
            headers=headers,
        )


class CodeSpectorReviewer:
    def __init__(
        self,
        diff_file: str,
        chat_token: str,
        chat_agent: str,
        chat_model: str | None,
        system_content: str,
        output_dir: str,
    ):
        self.diff_file = diff_file
        self.chat_token = chat_token
        self.chat_agent = chat_agent
        self.chat_model = chat_model
        self.system_content = system_content
        self.output_dir = output_dir

        self.request_file = 'request.json'
        self.response_file = 'response.json'
        self.result_file = 'result.txt'

    def _request_to_chat_agent(self, prompt: str):
        agent_info = AgentInfo.create(self.chat_agent, self.chat_token, self.chat_model)
        request_data = {
            'model': agent_info.model,
            'messages': [{'role': 'system', 'content': self.system_content}, {'role': 'user', 'content': prompt}],
        }

        with open(os.path.join(self.output_dir, self.request_file), 'w', encoding='utf-8') as f:
            ujson.dump(request_data, f, indent=4, ensure_ascii=False)

        response = requests.post(
            agent_info.url,
            json=request_data,
            headers=agent_info.headers,
            timeout=100,
        )
        response.raise_for_status()
        return response

    def send_to_review(self):
        with open(os.path.join(self.output_dir, self.diff_file), 'r', encoding='utf-8') as f:
            diff_data = ujson.load(f)

        diff_content = diff_data.get('diff', '')
        original_files = diff_data.get('original files', [])

        original_files_str = ujson.dumps(original_files, indent=4, ensure_ascii=False)

        prompt = (
            'Пожалуйста, проверь следующие изменения в коде на наличие очевидных проблем с качеством или безопасностью. '
            'Предоставь краткий отчет в формате markdown:\n\n'
            'DIFF:\n'
            f'{diff_content}\n\n'
            'ORIGINAL FILES:\n'
            f'{original_files_str}'
        )
        try:
            response = self._request_to_chat_agent(prompt=prompt)
        except Exception as e:
            logger.error('Error while send request: {}', e)
            raise e

        with open(os.path.join(self.output_dir, self.response_file), 'w', encoding='utf-8') as f:
            ujson.dump(response.json(), f, indent=4, ensure_ascii=False)

        resp = response.json()
        clear_response = resp['choices'][0]['message']['content']

        with open(os.path.join(self.output_dir, self.result_file), 'w', encoding='utf-8') as f:
            f.write(clear_response)

    def start(self):
        self.send_to_review()
