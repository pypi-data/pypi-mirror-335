import logging
from rich.logging import RichHandler

def set_simple_agent_logging():
    '''Sets some default values to get nice logging for agent tasks.'''
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('afasask.gpt.prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('ui_msg_actions').setLevel(logging.ERROR)
    logging.getLogger('afasask.chat.ui_msg_actions').setLevel(logging.ERROR)
    logging.getLogger('msg_manager').setLevel(logging.ERROR)
    logging.getLogger('afasask.chat.msg_manager').setLevel(logging.ERROR)
    logging.getLogger('_client').setLevel(logging.ERROR)
    logging.getLogger('openai').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)