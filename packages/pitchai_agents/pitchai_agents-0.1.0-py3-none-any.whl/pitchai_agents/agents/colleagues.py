from functools import partial
from uuid import uuid4
import asyncio
from code_ops.treemap import create_treemap
from agent.async_partial import async_partial

async def create_colleague_partials(repo_path: str, interpreter_path: str, agent_id: str = None, communication_callback=None):
    """Creates partial functions for each specialized agent with default arguments."""
    from agent.agents import codebase_answer_agent, dev_agent, webagent, infra_agent

    treemap = create_treemap(repo_path)

    if agent_id is None:
        agent_id = uuid4().hex  # fallback if none provided

    

    # A developer: answers questions about the codebase
    ask_developer = await async_partial(
        codebase_answer_agent.run_agent,
        max_steps=20,
        min_steps=3,
        treemap=treemap,  # or pass a default treemap
        repo_path=repo_path,
        interpreter_path=interpreter_path,
        surpress_logs=True,
        agent_id=f"{agent_id}-qdev",
        communication_callback=communication_callback
    )

    # A dev agent: performs development tasks in the codebase
    give_dev_task = await async_partial(
        dev_agent.run_agent,
        max_steps=70,
        treemap=treemap,
        repo_path=repo_path,
        interpreter_path=interpreter_path,
        agent_id=f"{agent_id}-dev",
        communication_callback=communication_callback
    )

    # A research agent: does web lookups / deeper research
    ask_researcher = await async_partial(
        webagent.run_agent,
        max_steps=20,
        min_steps=3,
        agent_id=f"{agent_id}-research",
        communication_callback=communication_callback
    )

    # An infra agent: handles infrastructure tasks
    give_infra_task = await async_partial(
        infra_agent.run_agent,
        max_steps=70,
        repo_path=repo_path,
        interpreter_path=interpreter_path,
        agent_id=f"{agent_id}-infra",
        communication_callback=communication_callback
    )

    # Return them as a dictionary
    return {
        'ask_developer': ask_developer,
        'give_dev_task': give_dev_task,
        'ask_researcher': ask_researcher,
        'give_infra_task': give_infra_task
    }


if __name__ == '__main__':
    async def main():
        partials = await create_colleague_partials(
            repo_path='.', interpreter_path='python3', agent_id='my_agent')
        tasks = [
            partials['ask_developer']('What is the purpose of this function?'),
            partials['give_dev_task']('Fix the bug in the login form'),
            partials['ask_researcher']('How do I use this library?'),
            partials['give_infra_task']('Set up a new server')
        ]
        results = await asyncio.gather(*tasks)
        print(results)

    asyncio.run(main())
