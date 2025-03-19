from code_ops.treemap import create_treemap
from markitdown import MarkItDown
import os
from uuid import uuid4
import asyncio

md = MarkItDown() 

global_repo_path_for_process = None
global_interpreter_path_for_process = None

async def ask_developer_question(question: str) -> str:
    '''Describes the codebase for a given query'''
    from agent.agents import codebase_answer_agent
    global global_repo_path_for_process
    global global_interpreter_path_for_process
    if not global_repo_path_for_process or not global_interpreter_path_for_process:
        raise Exception('Please set the global_repo_path_for_process and global_interpreter_path_for_process before calling this function')

    treemap = create_treemap(global_repo_path_for_process)

    previous_cwd = os.getcwd()
    os.chdir('/Users/sethvanderbijl/PitchAI Code/agents')
    try:
        output_summary = await codebase_answer_agent.run_agent(max_steps=20, min_steps=3, question=question, treemap=treemap, repo_path=global_repo_path_for_process, interpreter_path=global_interpreter_path_for_process, surpress_logs=True, agent_id=uuid4().hex)
    except Exception as e:
        output_summary = f'ERROR: {e}'
    os.chdir(previous_cwd)
    # Print to be sure, sometimes agents forgets to print explicitly
    print(output_summary)

    return output_summary


async def give_developer_dev_task(goal: str) -> str:
    '''Completes some task in a codebase'''
    from agent.agents import dev_agent
    global global_repo_path_for_process
    global global_interpreter_path_for_process
    if not global_repo_path_for_process or not global_interpreter_path_for_process:
        raise Exception('Please set the global_repo_path_for_process and global_interpreter_path_for_process before calling this function')
    
    treemap = create_treemap(global_repo_path_for_process)

    previous_cwd = os.getcwd()
    os.chdir('/Users/sethvanderbijl/PitchAI Code/agents')
    try:
        output_summary = await dev_agent.run_agent(max_steps=70, min_steps=3, global_goal=goal, treemap=treemap, repo_path=global_repo_path_for_process, interpreter_path=global_interpreter_path_for_process, surpress_logs=True, agent_id=uuid4().hex)
    except Exception as e:
        output_summary = f'ERROR: {e}'
    os.chdir(previous_cwd)
    # Print to be sure, sometimes agents forgets to print explicitly
    print(output_summary)

    return output_summary

async def ask_researcher_question(question: str) -> str:
    '''Does deep web research for a certain issue'''
    from agent.agents import webagent
    global global_repo_path_for_process
    global global_interpreter_path_for_process
    if not global_repo_path_for_process or not global_interpreter_path_for_process:
        raise Exception('Please set the global_repo_path_for_process and global_interpreter_path_for_process before calling this function')

    previous_cwd = os.getcwd()
    os.chdir('/Users/sethvanderbijl/PitchAI Code/agents')
    try:
        output_summary = await webagent.run_agent(max_steps=20, min_steps=3, global_goal=question, agent_id=uuid4().hex)
    except Exception as e:
        output_summary = f'ERROR: {e}'
    os.chdir(previous_cwd)
    # Print to be sure, sometimes agents forgets to print explicitly
    print(output_summary)

    return output_summary

async def give_infra_task_or_question(goal: str) -> str:
    '''Completes some task in a codebase'''
    from agent.agents import infra_agent


    previous_cwd = os.getcwd()
    os.chdir('/Users/sethvanderbijl/PitchAI Code/agents')
    try:
        output_summary = await infra_agent.run_agent(max_steps=70, min_steps=3, global_goal=goal, repo_path=global_repo_path_for_process, interpreter_path=global_interpreter_path_for_process, surpress_logs=True, agent_id=uuid4().hex)
    except Exception as e:
        output_summary = f'ERROR: {e}'
    os.chdir(previous_cwd)
    # Print to be sure, sometimes agents forgets to print explicitly
    print(output_summary)

    return output_summary



if __name__ == '__main__':
    # Example usage
    question = "What is the codebase about?"
    output_summary = asyncio.run(ask_developer_question(question))
    print(output_summary)
