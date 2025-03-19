from code_ops.git_ops import get_diffed_files_string
from code_ops.aexec import async_execute_catch_logs_errors, aexec_catch_logs_errors_codestrings
from code_ops.splitoff import try_splitoff_all_code_blocks, common_codeblock_markers, remove_all
from utils.string_shortening import shorten_all_strings_in_dict
from agent.history import summarize_history
from agent.report.update_report import update_report
from agent.tools.main import write_all_tools_to_globals
from agent.log_feedback import default_feedback_logs
from agent.max_step import time_almost_up_warning
from chat.ui_msg_actions import UIMsgActions
from code_ops.treemap import create_treemap
from agent.completion import stop_if_allowed
from code_ops.git_ops import get_untracked_files

from uuid import uuid4
import asyncio
import logging
import sys
from git import Repo

async def create_or_update_unittests(repo_path:str, global_goal:str, extra_info: str):
    msg_actions = await UIMsgActions.create(headless=True)

    # Goal, diffed files, extra_info (error in test?), existing unittests
    diffed_files_str = get_diffed_files_string(repo_path)
    untracked_files = get_untracked_files(Repo(repo_path))
    test_already_created = ''
    for filepath, content in untracked_files:
        if 'test_' in filepath:
            test_already_created += f'\n\n{filepath}\n\n```python{content}```'


    # Existing OK? -> return
    test_reasoning = await msg_actions.run_action(prompt_path='testing_strategy', 
                           prompt_format_kwargs={'goal': global_goal, 'diffed_files': diffed_files_str, 'extra_info': extra_info, 'test_already_created': test_already_created}, 
                           model='deepseek/r1', silent=False)
    

    # Generate or update tests
    res = await msg_actions.run_action(prompt_path='write_tests', 
                           prompt_format_kwargs={'goal': global_goal, 'diffed_files': diffed_files_str, 'extra_info': extra_info, 'test_reasoning': test_reasoning, 'test_already_created': test_already_created}, 
                           model='deepseek/r1', silent=False)
    
    code_blocks = try_splitoff_all_code_blocks(res)

    # test

    # First line of each codeblock should be the filepath
    filepaths_and_code = [(code.split('\n')[0], code) for code in code_blocks]

    # Now write each of these codeblocks to the respective file
    for filepath, code in filepaths_and_code:
        try:
            filepath = filepath.split('#')[1].strip()
            with open(filepath, 'w') as f:
                f.write(code)
        except Exception as e:
            print(f'Error writing unittest to file: {filepath}')
            print(e)

    # Create test for each component


if __name__ == '__main__':
    asyncio.run(create_or_update_unittests(repo_path='.', global_goal='Create or update unit tests', extra_info=''))