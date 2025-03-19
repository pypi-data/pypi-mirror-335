from agent.report.md_headers import get_headers
from chat.ui_msg_actions import UIMsgActions
from typing import List
import logging

logger = logging.getLogger(__name__)


def follows_correct_format(relevant_header):
    '''Checks whether the string is a point-separated number {space} text'''
    if not relevant_header:
        return False
    
    # Split by the first space only
    number_part, title_part = relevant_header.split(' ', 1)

    if not number_part:
        return False
    
    if not title_part:
        return False
    
    if not number_part.replace('.', '').isdigit():
        return False
    
    return True


async def get_relevant_header(md_report: str, given_text: str, msg_actions:UIMsgActions = None, conversation_id:str='test', headless: bool=True) -> str:
    """
    Returns all headers that are relevant to add the given text to.
    """
    
    # Start by getting the headers in the report
    headers = get_headers(md_report)

    # Create msg actions if not given
    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    retries = 0

    relevant_header = ''
    while not follows_correct_format(relevant_header):
        _, tool_args = await msg_actions.run_action(action_id=f'relevant_header', prompt_path='relevantheaders', prompt_format_kwargs={'given_text': given_text, 'headers': headers}, model='gemini-2.0-flash', silent=False)

        relevant_header = tool_args['relevant_header']

        retries += 1
        if retries > 3:
            logger.error(f"Failed to get relevant header after 3 retries. Returning None.")
            return None

    return relevant_header



if __name__ == '__main__':
    import asyncio
    markdown_string = """
# Vehicles
Paragraph under header 1.

## Cars
Paragraph under header 1.1.
More text under header 1.1.

## Boats
Paragraph under header 1.2.

# Houses
Paragraph under header 2.
    """

    print(asyncio.run(get_relevant_header(markdown_string, "The Ocean is wide and great")))