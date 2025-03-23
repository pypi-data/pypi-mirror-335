from pathlib import Path

import click
from environs import Env

from .controller import CodeSpectorController
from loguru import logger

BASE_PATH = Path(__file__).parent.parent

env = Env()
env.read_env(path=str(BASE_PATH / '.env'))


@click.option(
    '--system-content',
    type=str,
    default='Ты код ревьювер. Отвечай на русском языке.',
    envvar='CODESPECTOR_SYSTEM_CONTENT',
    show_envvar=True,
    help='Content which used in system field for agent',
)
@click.option(
    '--output-dir',
    type=str,
    default='codespector',
    envvar='CODESPECTOR_OUTPUT_DIR',
    show_envvar=True,
    help='Select the output directory',
)
@click.option(
    '-b',
    '--compare-branch',
    type=str,
    default='develop',
    help='Select the branch to compare the current one with',
)
@click.option(
    '--chat-agent',
    type=click.Choice(['codestral', 'chatgpt'], case_sensitive=False),
    envvar='CODESPECTOR_CHAT_AGENT',
    show_envvar=True,
    default='codestral',
    help='Choose the chat agent to use',
)
@click.option(
    '--chat-model',
    type=str,
    envvar='CODESPECTOR_CHAT_MODEL',
    show_envvar=True,
    help='Choose the chat model to use',
)
@click.option(
    '--chat-token',
    type=str,
    envvar='CODESPECTOR_CHAT_TOKEN',
    show_envvar=True,
)
@click.option(
    '--mode',
    type=click.Choice(['local'], case_sensitive=False),
    default='local',
    help='Choose the mode of the application',
)
@click.version_option(message='%(version)s')
@click.command()
def main(*args, **kwargs):
    return start(*args, **kwargs)


def start(*args, **kwargs):
    codespector = CodeSpectorController(*args, **kwargs)
    try:
        codespector.start()
        logger.info('Review completed successfully.See result.txt in {} directory', kwargs['output_dir'])
    except Exception as e:
        logger.error('Error while review: {}', e)


if __name__ == '__main__':
    main()
