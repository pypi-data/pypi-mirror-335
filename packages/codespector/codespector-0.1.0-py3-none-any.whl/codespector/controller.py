from codespector import local
from loguru import logger


class CodeSpectorController:
    __slots__ = (
        'mode',
        'chat_token',
        'chat_agent',
        'compare_branch',
        'output_dir',
        'system_content',
        'chat_model',
    )

    def __init__(
        self,
        mode: str,
        chat_token: str,
        chat_agent: str,
        compare_branch: str,
        output_dir: str,
        system_content: str,
        chat_model: str,
    ):
        self.mode = mode
        self.chat_token = chat_token
        self.chat_agent = chat_agent
        self.compare_branch = compare_branch
        self.output_dir = output_dir
        self.system_content = system_content
        self.chat_model = chat_model

    def start(self):
        codespector = local.LocalCodespector(
            chat_token=self.chat_token,
            chat_agent=self.chat_agent,
            compare_branch=self.compare_branch,
            output_dir=self.output_dir,
            system_content=self.system_content,
            chat_model=self.chat_model,
        )
        codespector.review()
        logger.info('Review completed successfully.See result.txt in {} directory', self.output_dir)
