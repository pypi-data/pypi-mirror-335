'''Same as dev agent but without unittests and timeupwarnings. '''

from code_ops.splitoff import try_splitoff_all_code_blocks, remove_all
from agent.history import summarize_history
from agent.report.update_report import update_report
from agent.tools.main import write_all_tools_to_globals
from agent.log_feedback import construct_log_from_config
from chat.ui_msg_actions import UIMsgActions
from code_ops.treemap import create_treemap
from agent.completion import stop_if_allowed
from server.task_config import TaskConfig
from uuid import uuid4
import asyncio
import logging
from code_ops.shell import aexec_catch_logs_errors_codestrings_shell
from code_ops.modify_string import insert_ssh_options

async def run_agent(max_steps: int = 6, repo_path='.', agent_id:str = '', headless=True, codebase_summary='', task_config: TaskConfig = None, treemap=None, build_report:bool=False, communication_callback=None, current_history=[], msg_actions=None, idle_shell_respond=5):    

    if not msg_actions:
        msg_actions = await UIMsgActions.create(headless=headless)

    for step_idx in range(max_steps+2):

        summarized_history: str = await summarize_history(task_config.goal, current_history, num_medium_summarized=3, num_unsummarized_final=7, agent_id=agent_id)

        # ACTION
        response = await msg_actions.run_action(prompt_path='infrastep', prompt_format_kwargs={'goal': task_config.goal, 'history': summarized_history, 'codebase_summary': codebase_summary})

        

        code_strings = try_splitoff_all_code_blocks(response, 'bash')
        code_strings += try_splitoff_all_code_blocks(response, 'console')
        code_strings += try_splitoff_all_code_blocks(response, 'shell')
        code_strings += try_splitoff_all_code_blocks(response, 'sh')

        # Single sent summary
        if communication_callback:
            single_sent_summary = await msg_actions.run_action(prompt_path='single_sent_status_update', prompt_format_kwargs={'latest_update': response, 'history': summarized_history, 'goal': task_config.goal}, model='gemini-2.0-flash-lite')
            single_sent_summary = try_splitoff_all_code_blocks(single_sent_summary, language='md')
            if single_sent_summary:
                single_sent_summary = single_sent_summary[0]
            formatted_codestrings = '\n'.join([f"```bash\n{code_str}\n```" for code_str in code_strings])
            log_str = f"-# Agent: {agent_id}  **Step: {step_idx}**\n {single_sent_summary} \n {formatted_codestrings}"
            await communication_callback(log_str)
        
        # EXECUTION
        logs = await aexec_catch_logs_errors_codestrings_shell(code_strings, task_config.project_path, idle_timeout=idle_shell_respond)
        if communication_callback:
            await communication_callback(f"```bash\n{code_strings[0] if code_strings else ''}\n```\n\n```console\n{logs}\n```")

        # Remove code str from response
        response = remove_all(response, code_strings)
        response = remove_all(response, ["```bash", '```'])

        
        # BUILD REPORT
        if logs and build_report:
            await update_report(f"{response}\n\n\n{logs}", global_goal=task_config.goal, report_path=f"agent/logs/reports/{agent_id}.md")

        # SAVE
        current_step_result_dict = {'thought': response, 'code': code_strings, 'logs': logs}
        current_history.append(current_step_result_dict)

        # STOP
        should_stop, ret_val = stop_if_allowed(code_str=response + '\n\n'.join(code_strings), logs=logs, current_history=current_history, repo_path=repo_path, interpreter_path=task_config.interpreter_path, step_idx=step_idx, max_steps=max_steps, additional_return_values=(current_history, summarized_history,))
        # Little hack since this agent dies Python c- some string
        if should_stop or 'complete_analysis(' in response + '\n'.join(code_strings):
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
    goal = '''We have 4 services in our docker compose. Check on the production server that all of them are actually running and if not what is the problem/error per service. Do not change anything, just check and describe it.'''
    goal = 'Please ensure that the crawler docker container is correctly runnng on the production server. Other services are not important so use a direct docker command not compose. Verify that it is crawling stuff. Locally (your env) we have a working build of the container already, but tjhis eeds to be pushed to docker and the pulled to the prod server I guess. And then the logs must be inspected whether it is actually crawling something. First find this locally built image/container.'


    goal = '''Please tell us exactly which websites are online (and which one crashed? offline?) on our production server.'''
    
    goal = 'Locally my 4 docker containers build and run fine without errors. The github actions also build but when we do docker compose on the production server we have for many of these services errors that should have been fixed in the newer builds? (as confirmed locally). Why am I seeing those old errors? Why do they work locally? You start locally (AI Price Crawler) by inspecing compose and build and deploy yamls. Then diagnose the problem for me.'
    task_config = TaskConfig(goal=goal, interpreter_path=interpreter_path, project_path=project_path)
    output_summary = asyncio.run(run_agent(max_steps=50, task_config=task_config, repo_path=project_path, agent_id=uuid4().hex, communication_callback=comm, idle_shell_respond=3))