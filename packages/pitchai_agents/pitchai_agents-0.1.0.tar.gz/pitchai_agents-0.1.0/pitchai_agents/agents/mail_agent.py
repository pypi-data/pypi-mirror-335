from code_ops.aexec import async_execute_catch_logs_errors
from code_ops.splitoff import try_splitoff_code_w_fallbacks, try_splitoff_all_code_blocks, common_codeblock_markers
from utils.string_shortening import shorten_all_strings_in_dict
from agent.report.update_report import update_report
from agent.history import summarize_history
from agent.tools.main import write_all_tools_to_globals
from agent.max_step import time_almost_up_warning
from utils.string_shortening import cutoff_str
from chat.ui_msg_actions import UIMsgActions
from rich.console import Console
from code_ops.treemap import create_treemap
from uuid import uuid4
import asyncio
import logging
import sys

console = Console()
logger = logging.getLogger(__name__)


async def run_agent(global_goal: str, max_steps: int = 6, min_steps=6,  conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, codebase_summary='', repo_path='.', interpreter_path=sys.executable, treemap=None, surpress_logs:bool = False,  return_hist: bool=False):
    
    current_history, current_globals = [], {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    for step_idx in range(max_steps):
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals = write_all_tools_to_globals(current_globals)

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        # TIME UP 
        global_goal += time_almost_up_warning(step_idx, max_steps)
        if step_idx > max_steps + 1:
            return response

        # ACTION
        response = await msg_actions.run_action(action_id=f'agent_{uuid4().hex}', prompt_path='mailstep', prompt_format_kwargs={'goal': global_goal, 'history': summarized_history, 'globals': shorten_all_strings_in_dict(current_globals), 'codebase_summary': codebase_summary}, model='gemini-2.0-flash')

        # CODE STR PREPROCESSING
        code_strings = try_splitoff_all_code_blocks(response, common_codeblock_markers)
        
        # EXECUTION
        logs = ''
        for code_str in code_strings: 
            current_globals, temp_logs = await async_execute_catch_logs_errors(code_str, current_globals, repo_path)
            logs += temp_logs

            # Remove code str from response
            response = response.replace(code_str, '').replace("```python\n```", "")

        # LOGS
        logs = cutoff_str(logs, max_words=20000)
        if not surpress_logs:
            console.log(f"Agent: {agent_id}, Step: {step_idx}, Thought: {response}", style='bold red')
            console.log(cutoff_str(logs, max_words=100), style='blue')


        if logs:
            await update_report(f"{response}\n\n\n{logs}", global_goal=global_goal, report_path=f"agent/logs/reports/{agent_id}.md")

        current_globals.pop('__builtins__', None)

        
        
        # SAVE
        current_step_result_dict = {'thought': response, 'code': code_strings, 'logs': logs, 'result': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        # STOP
        if 'complete_analysis(' in code_str:
            res = try_splitoff_code_w_fallbacks(logs, ["```finalanswermarkdown"]) + f"\n\n{current_history[-1]['thought']}"
            if return_hist:
                return res, current_history
            return res
      

        


if __name__ == '__main__':
    from rich.logging import RichHandler
    import os

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('afasask.gpt.prompt_loader').setLevel(logging.ERROR)

    goal = '''What was recent feedback on afasask for the gzb??'''
    output_summary = asyncio.run(run_agent(max_steps=50, min_steps=6, global_goal=goal, surpress_logs=False, agent_id=uuid4().hex))


