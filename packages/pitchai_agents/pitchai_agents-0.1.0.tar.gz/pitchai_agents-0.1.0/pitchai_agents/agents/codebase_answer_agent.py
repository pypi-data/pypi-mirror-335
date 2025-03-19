from code_ops.aexec import async_execute_catch_logs_errors
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from utils.string_shortening import shorten_all_strings_in_dict
from agent.history import summarize_history
from agent.tools.read import read_file
from agent.tools.web import google_search, read_document
from code_ops.modify_string import check_for_forbidden_definitions, check_forbidden_string
from agent.completion import complete_analysis
from agent.max_step import time_almost_up_warning
from utils.string_shortening import cutoff_str
from chat.ui_msg_actions import UIMsgActions
from rich.console import Console
from uuid import uuid4
import asyncio
import logging
import json
import sys


console = Console()
logger = logging.getLogger(__name__)


async def run_agent(question: str, max_steps: int = 6, min_steps=6,  conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, codebase_summary='', repo_path='.', interpreter_path=sys.executable, treemap=None, surpress_logs=False, communication_callback=None):
    
    current_history = []
    # Initialize empty globals, but provide the request_user_input function
    current_globals = {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id, headless=headless)

    step_idx = 0
    while True:
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals['complete_analysis'] = complete_analysis
        current_globals['read_document'] = read_document
        current_globals['google_search'] = google_search
        current_globals['read_file'] = read_file

        summarized_history: str = await summarize_history(question, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        # TIME UP 
        question += time_almost_up_warning(step_idx, max_steps)
        if step_idx > max_steps + 1:
            return response

        # ACTION
        response = await msg_actions.run_action(action_id=f'agent_{uuid4().hex}', prompt_path='codebaseresearch', prompt_format_kwargs={'goal': question, 'history': summarized_history, 'globals': shorten_all_strings_in_dict(current_globals), 'treemap': json.dumps(treemap, indent=2)}, model='gemini-2.0-flash')
        
        # CODE STR PREPROCESSING
        code_str = try_splitoff_code_w_fallbacks(response, ['```python', '```tool_code'], '```')
        non_code_response = response.replace(code_str, '')
        if not surpress_logs:
            console.log(f"Agent: {agent_id}, Step: {step_idx}, Thought: {non_code_response}", style='bold red')
            log_str = f"-# Agent: {agent_id}\n## Step: {step_idx}\n\n **Thought:** {non_code_response}"
            if communication_callback:
                await communication_callback(f"{log_str}")
        # console.log(code_str)

        # EXECUTION
        current_globals, logs = await async_execute_catch_logs_errors(code_str, current_globals, repo_path)
        current_globals.pop('__builtins__', None)
        # if logs:
        #     await update_report(f"{non_code_response}\n\n\n{logs}", global_goal)

        # LOGS
        logs = logs.replace('----', '')
        if not surpress_logs:
            console.log(cutoff_str(logs, max_words=400), style='blue')
            
        
        # SAVE
        current_step_result_dict = {'thought': non_code_response, 'code': code_str, 'logs': logs, 'result': shorten_all_strings_in_dict(current_globals)}
        current_history.append(current_step_result_dict)

        forbidden_redefines = check_for_forbidden_definitions(code_str, forbidden_funcs=['read_document', 'google_search', 'read_file'])
        if forbidden_redefines:
            logs += f"\n### Warning from manager:\n\n'''{forbidden_redefines}'''\n"


        # STOP
        if 'complete_analysis(' in code_str and not forbidden_redefines:
            if step_idx < min_steps:
                logs += f"Minimum number of steps not reached. You need to take at least {min_steps} steps. You have taken {step_idx}. You need to research much deeper and much less superficially. You need to take more steps and go deeper into the analysis."
            else:
                answer= try_splitoff_code_w_fallbacks(logs, ["```finalanswermarkdown"], '```') + f"\n\n{current_history[-1]['thought']}"
                return answer
      
        step_idx += 1

        


if __name__ == '__main__':
    from rich.logging import RichHandler
    from code_ops.treemap import create_treemap
    import os

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('afasask.gpt.prompt_loader').setLevel(logging.ERROR)

    treemap = create_treemap(os.getcwd())

    print(treemap)
    
    question = "How does SSE streaming work in this Codebase?"
    
    output_summary = asyncio.run(run_agent(max_steps=50, min_steps=6, question=question, treemap=treemap, repo_path=os.getcwd()))
