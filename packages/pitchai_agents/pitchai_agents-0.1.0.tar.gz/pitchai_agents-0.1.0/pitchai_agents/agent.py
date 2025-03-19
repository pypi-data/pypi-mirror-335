from code_ops.exec import execute_catch_logs_errors
from agent.history import summarize_history
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from utils.string_shortening import shorten_all_strings_in_dict, cutoff_str
from code_ops.modify_string import remove_spark_stop, replace_show_calls_w_untruncated_show
from agent.completion import complete_analysis
from chat.ui_msg_actions import UIMsgActions
from code_ops.modify_string import rewrite_spark_session_creation
import asyncio
from gpt.prompt_loader import PromptLoader
import json
from uuid import uuid4
import logging
from code_ops.extract_spark import extract_spark_session

logger = logging.getLogger(__name__)


# Create additional info
base_info = PromptLoader().load_prompt('prompts/base_info.md')

async def run_agent(global_goal: str, schema: str, max_steps: int = 6, conversation_id: str = '', msg_actions: UIMsgActions = None, return_history=False, agent_id:str = '', advice_mode: bool  = True, base_info='', return_dfs=False):
    current_history = []
    # Initialize empty globals, but provide the request_user_input function
    current_globals = {}

    if not msg_actions:
        msg_actions = await UIMsgActions.create(conversation_id=conversation_id)

    # Set up some global prompts
    if advice_mode:
        global_goal = f"A data-analyst for the GZB (gereformeerde zendingsbond) will analyse the local pyspark parquet file and answer the following query based on his python pyspark analysis of the dataframe: '''{global_goal}'''. It is your job to do some exploratory pre-analysis using pyspark and to note down some important findings, pitfalls, etecetera that your friend might encounter when doing a pyspark analysis of this dataframe. (For example is the search string as expected?, etc.). You must load it with pyspark and do not do the anlysis to answer the full query yet. Just do some exploratory analysis and note down some important findings, pitfalls, etc. that your friend might encounter when doing the analysis. Use pyspark in code. Make sure your suggestions are actual helpful like inding the true column and true search string that should be used for example by iteratitvely narrowing the unique values in a column or using like. Take an iterative approach dont try to get all facts all at once. So execute a little piece of code, read it, execute a new piece based on what youve learned, etc. So do some exploratory pre-analysis so that in the end you can advice the data-analyst about how he should approach the data-analysis. Make sure your suggestions are actual helpful like finding the true column and true search string that should be used for example by iteratively narrowing the unique values in a column or using like. Take an iterative approach don't try to get all facts all at once. So execute a little piece of code, read it, execute a new piece based on what you've learned, etc. Make sure you actually have, in the end of the process, completed the analysis once yourself. Then you will be best at advising."
    else:
        global_goal = f"You are a  data-analyst for the GZB (gereformeerde zendingsbond). You must step-by-step perform a data-analysis to answer the following question/ query based on his python pyspark analysis of the dataframe: '''{global_goal}'''. Use pyspark in code.  Take an iterative approach dont try to get all facts all at once.  So execute a little piece of code, read it, execute a new piece based on what youve learned, etc. Make sure to in the end complete the full analysis that answers the query/question."
    
    summarized_start_info = base_info


    step_idx = 0
    while True:
        # Make sure that the functions are not overwritten in the globals (or that they are set)
        current_globals['complete_analysis'] = complete_analysis

        summarized_history: str = await summarize_history(global_goal, current_history, num_medium_summarized=7, num_unsummarized_final=4, agent_id=agent_id)

        if step_idx == max_steps-2:
            global_goal += "\n\nAt this point you have one step left. Make sure to wrap up here and give the best advice you got. You can take 1 more step so use it wisely and do not waste it on detailed reesearch. Just 1 global thing you can still research before you'll have to answer. So think about you want to do, the only thing you can do before returning your final answer."

        if step_idx == max_steps:
            global_goal += '\n\nAt this point you have used up ALL your time and steps. So the previous advice is overriden. You MUST finish now. You must call complete_analysis in your code now, not later. You must wrap up the process.'

        if step_idx > max_steps + 1:
            return response

        response = await msg_actions.run_action(action_id=f'agent_{uuid4().hex}', prompt_path='codestep', prompt_format_kwargs={'goal': global_goal, 'additional_info': summarized_start_info, 'history': summarized_history, 'globals': shorten_all_strings_in_dict(current_globals), 'schema': json.dumps(schema, indent=2)}, silent=True, model='gemini-2.0-flash', header_text=f"{agent_id}: {current_history[-1]['thought'][:350]}..." if current_history else f'{agent_id} Diep onderzoeken...', overwrite_postfix=True)
        
        # We need to catch cases were ```tool_code is used rather than python (probably how gemini was finetuned)
        code_str = try_splitoff_code_w_fallbacks(response, ['```python', '```tool_code'], '```')
        non_code_response = response.replace(code_str, '')

        logger.info(f"Agent: {agent_id}, Step: {step_idx}")
        logger.debug(f"Thought: {non_code_response}")

        code_str = remove_spark_stop(code_str)
        logger.debug(code_str)
        await msg_actions.ui_msg.stream_into('<i class="fa-solid fa-spinner fa-spin"></i> Ik voer een analyse uit...', 'postfix', overwrite=True)
        code_str = rewrite_spark_session_creation(code_str)

        execution_result, logs = execute_catch_logs_errors(code_str, current_globals)
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
            # We make sure the previous code step is fully printed
            previous_code_str = replace_show_calls_w_untruncated_show(current_history[-1]['code'])
            if previous_code_str != current_history[-1]['code']:
                _, previous_logs = execute_catch_logs_errors(previous_code_str, current_globals)
                # Only rewrite history if we didn't introduce erros
                if not 'ERROR' in previous_logs:
                    previous_logs = previous_logs.replace('----', '')
                    previous_logs = cutoff_str(previous_logs)
                    current_history[-1]['logs'] = previous_logs
                    current_history[-1]['code'] = previous_code_str

            response = f"Last step before completing analysis was:{current_history[-1]}\n\nFinal result of the analysis was:\n\n{current_step_result_dict}"
            
            if not return_dfs:
                return response
            else:
                try:
                    dfs = extractor.extract_all_dataframes_with_keys(current_globals)
                    df_paths = save_dfs_to_disk(conversation_id, dfs, agent_id)
                    # Clear cache to make other data-analyses not so slow
                    spark = extract_spark_session(current_globals)
                    if spark:
                        spark.catalog.clearCache()
                except Exception as e:
                    logger.error(f"Error extracting dataframes: {e}")
                return response
      

        step_idx += 1

        


if __name__ == '__main__':
    with open('afasask/schema/db_schema.json', 'r') as f:
        schema = json.load(f)
    schema = schema['schema']['Financial_mutations']

    asyncio.run(run_agent(global_goal="A friend will analyse the local pyspark parquet file 'afasask/connectors/afas/denormalized_files/Financial_mutations.parquet' and answer the following query based on his python pyspark analysis of the dataframe: 'Wat is de dekkingsgraad van zendingswerker Corine Godeschalk per jaar?'", schema=json.dumps(schema, indent=2, default=str)))