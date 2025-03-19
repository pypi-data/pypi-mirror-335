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
from agent.dynamic_unittest import create_or_update_unittests
from agent.async_partial import async_partial
from uuid import uuid4
import asyncio
import logging
import sys

async def run_agent(global_goal: str, max_steps: int = 6, conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, codebase_summary='', repo_path='.', interpreter_path=sys.executable, treemap=None, return_hist: bool=False, build_report:bool=False, communication_callback=None):    
    current_history, current_globals = [], {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    create_or_update_unittests_partial = await async_partial(create_or_update_unittests, repo_path=repo_path, global_goal=global_goal)

    for step_idx in range(max_steps+2):
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals = write_all_tools_to_globals(current_globals)
        current_globals.update({'create_or_update_unittests': create_or_update_unittests_partial})

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        # TIME UP
        global_goal += time_almost_up_warning(step_idx, max_steps)

        model = 'gemini-2.0-flash'
        # Every 4th step set model to deepseek/r1
        if step_idx % 4 == 0:
            model = 'deepseek/r1'

        # Design unittests on the 3rd step
        if step_idx == 3:
            await create_or_update_unittests_partial(extra_info='Design good unittests')

        # ACTION
        response = await msg_actions.run_action(prompt_path='devstep', prompt_format_kwargs={'goal': global_goal, 'history': summarized_history, 'treemap': treemap, 'globals': shorten_all_strings_in_dict(current_globals), 'codebase_summary': codebase_summary}, model=model)

        # CODE STR PREPROCESSING
        code_strings = try_splitoff_all_code_blocks(response)
        
        # EXECUTION
        current_globals, logs = await aexec_catch_logs_errors_codestrings(code_strings, current_globals, repo_path)

        # Remove code str from response
        response = remove_all(response, code_strings)
        response = remove_all(response, common_codeblock_markers + ['```'])

        # LOGS
        logs = default_feedback_logs(logs, code_strings=code_strings, interpreter=interpreter_path, repo_path=repo_path, agent_id=agent_id)
        log_str = f"-# Agent: {agent_id}\n## Step: {step_idx}\n\n **Thought:** {response}"
        if communication_callback:
            await communication_callback(log_str)

        # BUILD REPORT
        if logs and build_report:
            await update_report(f"{response}\n\n\n{logs}", global_goal=global_goal, report_path=f"agent/logs/reports/{agent_id}.md")

        # SAVE
        current_step_result_dict = {'thought': response, 'code': code_strings, 'logs': logs, 'result': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        # STOP
        should_stop, ret_val = stop_if_allowed(code_str=response + '\n\n'.join(code_strings), logs=logs, current_history=current_history, repo_path=repo_path, interpreter_path=interpreter_path, step_idx=step_idx, max_steps=max_steps)
        if should_stop:
            return ret_val
      



if __name__ == '__main__':
    from rich.logging import RichHandler

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('afasask.gpt.prompt_loader').setLevel(logging.ERROR)

    async def comm(msg):
        print(msg)

    project_path = "/Users/sethvanderbijl/PitchAI Code/AI Price Crawler"
    interpreter_path = "/Users/sethvanderbijl/Library/Caches/pypoetry/virtualenvs/ai_price_crawler-6CKRPcSL-py3.11/bin/python"
    treemap = create_treemap(project_path)
    goal = '''please check that the meilisearch adder script works correctly.'''
    output_summary = asyncio.run(run_agent(max_steps=50, global_goal=goal, treemap=treemap, repo_path=project_path, agent_id=uuid4().hex, interpreter_path=interpreter_path, communication_callback=comm))