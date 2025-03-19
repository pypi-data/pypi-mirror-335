from code_ops.aexec import async_execute_catch_logs_errors
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from code_ops.modify_string import check_for_forbidden_definitions
from utils.string_shortening import cutoff_str, shorten_all_strings_in_dict
from agent.history import summarize_history
from agent.completion import complete_analysis
from chat.ui_msg_actions import UIMsgActions
from uuid import uuid4
import asyncio
import logging
import json
import os

logger = logging.getLogger(__name__)



async def run_agent(global_goal: str, max_steps: int = 6, min_steps=6,  conversation_id: str = '', msg_actions: UIMsgActions = None, agent_id:str = '', headless=True, treemap: dict = None, repo_path='.'):
    from agent.tools import read_document, google_search, read_file

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

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=3, agent_id=agent_id)

        if step_idx == max_steps-2:
            global_goal += "\n\nAt this point you have one step left. Make sure to wrap up here and give the best advice you got. You can take 1 more step so use it wisely and do not waste it on detailed reesearch. Just 1 global thing you can still research before you'll have to answer. So think about you want to do, the only thing you can do before returning your final answer."

        if step_idx == max_steps:
            global_goal += '\n\nAt this point you have used up ALL your time and steps. So the previous advice is overriden. You MUST finish now. You must call complete_analysis in your code now, not later. You must wrap up the process.'

        if step_idx > max_steps + 1:
            return response

        response = await msg_actions.run_action(action_id=f'agent_{uuid4().hex}', prompt_path='codereadstep', prompt_format_kwargs={'goal': global_goal, 'history': summarized_history, 'globals': shorten_all_strings_in_dict(current_globals), 'treemap': json.dumps(treemap, indent=2)}, model='gemini-2.0-flash', header_text=f"{agent_id}: {current_history[-1]['thought'][:350]}..." if current_history else f'{agent_id} Diep onderzoeken...', overwrite_postfix=True)
        
        # We need to catch cases were ```tool_code is used rather than python (probably how gemini was finetuned)
        code_str = try_splitoff_code_w_fallbacks(response, ['```python```', '```python', '```tool_code'], '```')
        non_code_response = response.replace(code_str, '')

        logger.info(f"Agent: {agent_id}, Step: {step_idx}, Thought: {non_code_response}")

        logger.debug(code_str)


        # Protect against overwriting function definitions
        forbidden_redefines = check_for_forbidden_definitions(code_str, forbidden_funcs=['complete_analysis', 'read_document', 'google_search', 'read_file'])
        if forbidden_redefines:
            logs = forbidden_redefines
            execution_result = current_globals
        else:
            # wrap code in async def
            # code_str = f"async def agent_code():\n{code_str}"
            execution_result, logs = await async_execute_catch_logs_errors(code_str, current_globals, repo_path)
            execution_result.pop('__builtins__', None)

        logs = logs.replace('----', '')
        logger.debug(logs)
        logs = cutoff_str(logs)

        current_globals = execution_result
        current_step_result_dict = {'thought': non_code_response, 'code': code_str, 'logs': logs, 'result': shorten_all_strings_in_dict(execution_result)}

        # Update history
        current_history.append(current_step_result_dict)

        # Check if the process should be stopped
        if 'complete_analysis()\n' in response:
            if step_idx < min_steps:
                logs += f"Minimum number of steps not reached. You need to take at least {min_steps} steps. You have taken {step_idx}. You need to research much deeper and much less superficially. You need to take more steps and go deeper into the analysis."
            else:
                response = f"Last step before completing analysis was:\n{current_history[-2]}\n\n\nFinal result of the analysis was:\n{current_step_result_dict}"
                return response
      
        step_idx += 1

        


if __name__ == '__main__':
    from rich.logging import RichHandler
    from code_ops.treemap import create_treemap

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    logging.getLogger('prompt_loader').setLevel(logging.ERROR)
    logging.getLogger('components.prompt_loader').setLevel(logging.ERROR)

    treemap = create_treemap(os.getcwd())

    print(treemap)
    
    goal = "Test analysis summary almost works. But I think the unittest is broken. Why? Please fix it, or fix the analysis summary component if it is broken."
    # output_summary = asyncio.run(run_agent(max_steps=50, min_steps=6, global_goal=goal, treemap=treemap))

    with open('codebase_summary.txt', 'w') as f:
        f.write(output_summary)
