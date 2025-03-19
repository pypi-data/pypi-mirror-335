'''Same as dev agent but without unittests and timeupwarnings. '''

from code_ops.aexec import aexec_catch_logs_errors_codestrings
from code_ops.splitoff import try_splitoff_all_code_blocks, common_codeblock_markers, remove_all
from utils.string_shortening import shorten_all_strings_in_dict
from agent.history import summarize_history
from agent.report.update_report import update_report
from agent.tools.main import write_all_tools_to_globals
from agent.log_feedback import default_feedback_logs, construct_log_from_config
from chat.ui_msg_actions import UIMsgActions
from code_ops.treemap import create_treemap
from agent.completion import stop_if_allowed
from code_ops.git_ops import get_diffed_files_string
from server.task_config import TaskConfig
from code_ops.git_ops import get_modified_files, revert_file_change
from uuid import uuid4
import asyncio
import logging
import sys

async def run_agent(max_steps: int = 6, repo_path='.', agent_id:str = '', headless=True, codebase_summary='', task_config: TaskConfig = None, treemap=None, build_report:bool=False, communication_callback=None, editable_filepaths=None, current_history=[], msg_actions=None):    
    current_globals =  {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(headless=headless)

    for step_idx in range(max_steps+2):
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals = write_all_tools_to_globals(current_globals)

        summarized_history: str = await summarize_history(task_config.goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)
        
        model = 'gemini-2.0-flash'
        # Every 4th step set model to deepseek/r1
        if step_idx == 0:
            model = 'deepseek/r1'

        # ACTION
        response = await msg_actions.run_action(prompt_path='devstep', prompt_format_kwargs={'goal': task_config.goal, 'history': summarized_history, 'treemap': treemap, 'globals': shorten_all_strings_in_dict(current_globals), 'codebase_summary': codebase_summary, 'interpreter': task_config.interpreter_path}, model=model)

        # CODE STR PREPROCESSING
        code_strings = try_splitoff_all_code_blocks(response)
        
        # EXECUTION
        current_globals, logs = await aexec_catch_logs_errors_codestrings(code_strings, current_globals, repo_path)
        
        # Remove code str from response
        response = remove_all(response, code_strings)
        response = remove_all(response, common_codeblock_markers + ['```'])

        # LOGS
        logs = construct_log_from_config(task_config, repo_path, logs, code_strings=code_strings, agent_id=agent_id)

        # Check for unallowed edited files
        for modified_file in get_modified_files(repo_path):
            print(modified_file)
            # if modified_file not in editable_filepaths:
                # revert_file_change(repo_path, modified_file)
                # logs+= f"Error: You tried to modify a file that you are not allowed to modify. You are not allowed to edit the file {modified_file}.\n The only files you may modify are: {editable_filepaths}"

        
        if communication_callback:
            single_sent_summary = await msg_actions.run_action(prompt_path='single_sent_status_update', prompt_format_kwargs={'latest_update': response, 'history': summarized_history, 'goal': task_config.goal}, model='gemini-2.0-flash-lite')
            single_sent_summary = try_splitoff_all_code_blocks(single_sent_summary, language='md')
            if single_sent_summary:
                single_sent_summary = single_sent_summary[0]
            log_str = f"-# Agent: {agent_id}  **Step: {step_idx}**\n {single_sent_summary}"
            await communication_callback(log_str)

        # BUILD REPORT
        if logs and build_report:
            await update_report(f"{response}\n\n\n{logs}", global_goal=task_config.goal, report_path=f"agent/logs/reports/{agent_id}.md")

        # SAVE
        current_step_result_dict = {'thought': response, 'code': code_strings, 'logs': logs, 'result': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        # STOP
        should_stop, ret_val = stop_if_allowed(code_str=response + '\n\n'.join(code_strings), logs=logs, current_history=current_history, repo_path=repo_path, interpreter_path=task_config.interpreter_path, step_idx=step_idx, max_steps=max_steps, additional_return_values=(current_history, get_diffed_files_string(repo_path), summarized_history,))
        if should_stop:
            return ret_val