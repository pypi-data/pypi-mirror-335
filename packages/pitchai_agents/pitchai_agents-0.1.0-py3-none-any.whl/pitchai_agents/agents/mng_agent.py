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
from agent.agents.colleagues import create_colleague_partials
from uuid import uuid4
import asyncio
import logging
import sys

async def run_agent(global_goal: str, max_steps: int = 6, conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, codebase_summary='', repo_path='.', interpreter_path=sys.executable, treemap=None, return_hist: bool=False, build_report:bool=False, communication_callback=None):    
    current_history, current_globals = [], {}

    colleagues_dict = await create_colleague_partials(repo_path=repo_path, interpreter_path=interpreter_path, communication_callback=communication_callback, agent_id=agent_id)

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    for step_idx in range(max_steps):
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals = write_all_tools_to_globals(current_globals)
        current_globals.update(colleagues_dict)

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        # TIME UP 
        global_goal += time_almost_up_warning(step_idx, max_steps)

        # ACTION
        response = await msg_actions.run_action(prompt_path='manager', prompt_format_kwargs={'goal': global_goal, 'history': summarized_history, 'treemap': treemap, 'globals': shorten_all_strings_in_dict(current_globals), 'codebase_summary': codebase_summary}, model='gemini-2.0-flash')

        # LOGS
        # logs = construct_logs(logs, code_strings=code_strings, interpreter=interpreter_path, repo_path=repo_path, agent_id=agent_id)
        log_str = f"-# Agent: {agent_id}\n # Manager \n\n ## Step: {step_idx}\n\n **Thought:**\n {response}"
        if communication_callback:
            await communication_callback(log_str)

        # CODE STR PREPROCESSING
        code_strings = try_splitoff_all_code_blocks(response, common_codeblock_markers)

        
        
        # EXECUTION
        current_globals, logs = await aexec_catch_logs_errors_codestrings(code_strings, current_globals, repo_path)
        if '''if __name__ == ''' in code_strings:
            logs += '# ERROR \n\nERROR: You tried to do if name is main. I have clearly told you that the code must be executed headless top-level. NO if name is main allowed. Just do top-level awaits.\n\n'

        # Remove code str from response
        response = remove_all(response, code_strings)
        response = remove_all(response, common_codeblock_markers + ['```'])

        

        # BUILD REPORT
        if logs and build_report:
            await update_report(f"{response}\n\n\n{logs}", global_goal=global_goal, report_path=f"agent/logs/reports/{agent_id}.md")

        # SAVE
        current_step_result_dict = {'thought': response, 'code': code_strings, 'logs': logs, 'current_globals': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        # STOP
        should_stop, ret_val = stop_if_allowed(code_str=response, logs=logs, current_history=current_history, return_hist=return_hist, repo_path=repo_path, interpreter_path=interpreter_path, step_idx=step_idx, max_steps=max_steps)
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
    goal = '''We have several docker services in this project and a docker compose file. Can you tests whether docker compose up works correctly and whether the services in it are running correctly?'''
    output_summary = asyncio.run(run_agent(max_steps=50, global_goal=goal, treemap=treemap, repo_path=project_path, agent_id=uuid4().hex, interpreter_path=interpreter_path, communication_callback=comm))