from agent.agents import webagent
import asyncio
from code_ops.treemap import create_treemap
from agent.utils import set_simple_agent_logging
import json
from code_ops.git_ops import discard_all_changes
from agent.questions.codebase_followup_subquestions import n_level_question_research
from chat.ui_msg_actions import UIMsgActions
    
async def reformulate_enrich_task(goal_or_question: str, project_path: str, communication_callback=None, msg_actions=None, context=''):
    '''This function reasons extensively to enrich and reformulate the task into an enriched plan. It is a high-level function that uses the agent framework to reason about the task and enrich it. It returns a list of tasks that are enriched.'''
    # 1. Set up some values
    if not msg_actions:
        msg_actions = await UIMsgActions.create(headless=True)

    treemap = create_treemap(project_path)

    # 2. Reason about how the task could be approached based on all available information (exploring different angles, etc.)
    reasoning_about_approach = await msg_actions.run_action(prompt_path='simplereason', prompt_format_kwargs={'task': goal_or_question,'context':context, 'treemap': json.dumps(treemap, indent=2)})
    if communication_callback:
        await communication_callback(reasoning_about_approach)

    context += f'\n\n {reasoning_about_approach}'

    # 3. Actually reason about how to formulate and formulate an enirched task
    _, tool_args = await msg_actions.run_action(prompt_path='formulate_task_detailed', prompt_format_kwargs={'task': goal_or_question,'context':context, 'treemap': json.dumps(treemap, indent=2)})
    if communication_callback:
        await communication_callback(f"## Title\n{tool_args['tasks_list'][0]['title']}")
        await communication_callback(f"## Goal\n{tool_args['tasks_list'][0]['goal']}")
        await communication_callback(f"## Context\n{tool_args['tasks_list'][0]['context']}")

    discard_all_changes(project_path)

    # Task list only has a single item normally
    return tool_args['tasks_list']






if __name__ == "__main__":
    # print("Arguments received:", sys.argv)
    # asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else None, sys.argv[2] if len(sys.argv) > 2 else 'crawler_dockerfiled2'))
    import uuid

    goal = """Now we will focus on the crawler dockerfile. It almost works but it says sometimes that it cant find the scrapy command and sometimes that this is not an actve scrapy project. How to fix this? I want a single developer working on this. Note that it is crucial that this developers actually builds and runs the container and checks the logs to verify whether it is actually working correctly. The dutyfree craawler must run. Make sure to isntruct your developer to actually test, build and log the docker container that results until it works."""
    # goal = "Please remove all files that are clearly outdated, not used anymore from the codebase."
    # goal = '''What is the next big thing that should be done in this codebase?'''
    goal = '''We can ALWAYS login to the server with " ssh -i ~/.ssh/github-actions-hetzner root@213.239.210.154". Please write a simple script that logs in to the server and checks and prints whether each of the docker compose services is running on the server?'''
    # goal  = '''Remove all files that are clearly outdated and not used anymore from the codebase. Be careful and conservative, only remove files that are not used anymore.'''

    goal = '''Write a great, explainative clear readme for this codebase and how it essentially unifies multiple services.'''

    goal = '''Build, run and check logs of the scrapy crawler docker container until it works correctly. dont start interactive sessions but you can always execute commands on the built container. You can check logs of a running container with docker logs --timestamps --tail 40 -f <container_id_or_name>'''
    goal  = '''Build, run and check logs of the match_dependent_ops docker container until it works correctly. dont start interactive sessions but you can always execute commands on the built container. product.name must be product.title. Make incisal changes only. test docker container with building, running and logging until you are sure it works.  You can check logs of a running container with docker logs --timestamps --tail 40 -f <container_id_or_name>'''
    async def aprint(msg):
        print(msg)

    res = asyncio.run(reformulate_enrich_task(goal, project_path='/Users/sethvanderbijl/PitchAI Code/AI Price Crawler', communication_callback=aprint))
