from code_ops.git_ops import get_modified_or_untracked_files, execute_recently_created_files, get_diffed_files_string
from code_ops.unittest_ops import run_pytest, which_files_missing_test_file
from code_ops.modify_string import check_for_forbidden_definitions, check_forbidden_string
from utils.string_shortening import cutoff_str
from gpt.prompt_loader import PromptLoader
from typing import List
from server.task_config import TaskConfig
import sys
import os
from functools import partial
from test_docker import build_run_read_logs

indent_log = PromptLoader().load_prompt("/Users/sethvanderbijl/PitchAI Code/agents/prompts/devstep/indent.md")


def construct_log_from_config(config: TaskConfig, clone_path, start_logs:str, code_strings:List[str], agent_id:str) -> str:
    '''Calls all feedback functions specified in the config, constructs the log and gives the logs back.
    
    
    Args:
        config (TaskConfig): The configuration for the task.
        start_logs (str): The logs to start with.
        code_strings (List[str]): The code strings to check for forbidden strings.
        agent_id (str): The agent id to check for incoming messages.
    '''

    func_map = {
        'get_diffed_files_string': partial(get_diffed_files_string, config.project_path),
        'get_modified_or_untracked_files': partial(get_modified_or_untracked_files, config.project_path),
        'execute_recently_created_files': partial(execute_recently_created_files, config.project_path, interpreter=config.interpreter_path),
        'run_pytest': partial(run_pytest, config.project_path, python_executable=config.interpreter_path),
        'which_files_missing_test_file': partial(which_files_missing_test_file, config.project_path),
        'docker': partial(build_run_read_logs, clone_path)
    }

    if len(config.feedback_mechanism_args) == 0:
        return default_feedback_logs(config, start_logs, code_strings, agent_id)

    for func in config.feedback_mechanism_args:
        
        
        
        if ':' not in func:
            if func not in func_map:
                raise ValueError(f"Function {func} not found in feedback functions.")
            start_logs += f"\n### {func} logs:\n\n'''{func_map[func]()}'''\n"
        else:
            func, args = func.split(':')
            if func not in func_map:
                raise ValueError(f"Function {func} not found in feedback functions.")
            args = args.split(',')
            start_logs += f"\n### {func} logs:\n\n'''{func_map[func](*args)}'''\n"
    
    return start_logs





def default_feedback_logs(config: TaskConfig, start_logs: str, code_strings: List[str], agent_id: str) -> str:
    '''Construct comprehensive log dict for the agent.'''
    repo_path = config.project_path
    interpreter = config.interpreter_path


    # Some preprocessing
    input_logs = start_logs.replace('----', '')

    logs = f"\n### Files you edited/added this sessiosn\n\n'''{get_diffed_files_string(repo_path)}'''\n"

    logs += f"\n### STDOUT of your code:\n\n'''{input_logs}'''\n"

    # Logs about files created/edited this run
    logs += f"\n### Modified files:\n\nIn your whole history you have edited these files {get_modified_or_untracked_files(repo_path)}\n"

    # Protect against overwriting function definitions
    for code_str in code_strings:
        forbidden_redefines = check_for_forbidden_definitions(code_str, forbidden_funcs=['read_document', 'google_search', 'read_file'])
        if forbidden_redefines:
            logs += f"\n### Warning from manager:\n\n'''{forbidden_redefines}'''\n"
        
        # Protect against forbidden strings (like emptying database)
        forbidden_code_strs = check_forbidden_string(code_str)
        if forbidden_code_strs:
            logs += f"\n### Warning from manager:\n\n'''{forbidden_code_strs}'''\n"

    # Logs about whether the files created actually run
    file_run_succes, file_run_logs = execute_recently_created_files(repo_path, interpreter=interpreter)
    logs += f"\n### Running your created file logs:\n\n'''{cutoff_str(file_run_logs, max_words=2000)}'''\n"

    if "IndentationError" in file_run_logs:
        logs += f"\n### Indentation error logs:\n\n'''{indent_log}'''\n"

    # KNOWN PROBLEM, endless pytests can freeze complete system for all agents
    # # Only add pytest logs if the files actually run
    # if file_run_succes:
    #     unit_test_result_str = run_pytest(repo_path, python_executable=interpreter)
    #     logs += f"""\n### Unittest logs:\n\n'''{cutoff_str(unit_test_result_str)}"""
    # else:
    #     logs += f"\n### Unittest logs:\n\n'''Unittests will be run once you resolve the other errors..'''\n"

    remarks_from_boss = read_and_empty_file(f'/Users/sethvanderbijl/PitchAI Code/agent/logs/incoming/{agent_id}_incoming.md')
    if remarks_from_boss:
        logs += f"\n### Remarks from the boss:\n\n'''{remarks_from_boss}'''\n"

    # ensure starts with normal title
    if not logs.startswith('## Logs'):
        logs = '## Logs\n' + logs

    return logs


def read_and_empty_file(filename):
    '''Reads a file and empties it.'''
    # Ensure the parent path exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # If it does not exist create it (empty)
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write('')
        return ''
    with open(filename, 'r') as f:
        content = f.read()
    with open(filename, 'w') as f:
        f.write('')
    return content



if __name__ == "__main__":
    task_config = TaskConfig.from_msg(1313804595046387714, msg='feedback:docker:aipc_match_ops,aipc_match_ops,/services/dockerfile-run-match-dependent-operations')

    print(task_config.feedback_mechanism_args)

    print(construct_log_from_config(task_config, '## Logs\n', ['print("Hello")'], 'test_agent'))