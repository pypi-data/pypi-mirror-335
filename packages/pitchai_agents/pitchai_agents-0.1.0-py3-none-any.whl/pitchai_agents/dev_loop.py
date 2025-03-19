
from chat.ui_msg_actions import UIMsgActions
from agent.agents import dev_agent, tech_lead
import asyncio
from code_ops.treemap import create_treemap
import os
from code_ops.git_ops import commit_changes, push_branch, create_pull_request, discard_all_changes
from code_ops.codebase import setup_worktree
from code_ops.splitoff import try_splitoff_code_w_fallbacks
from agent.questions.codebase_followup_subquestions import n_level_question_research
from uuid import uuid4


async def start_dev_until_succeed(goal: str, project_path:str, interpreter_path: str, communication_callback=None, start_branch=uuid4().hex, agent_id=uuid4()):

    actions = UIMsgActions(conversation_id='dev_loop', headless=True)

    current_task = goal
    qa_list  = await n_level_question_research(goal, project_path, interpreter_path, communication_callback, treemap, msg_actions=actions)
    current_task = str(await tech_lead.reformulate_enrich_task(goal_or_question=goal, project_path=project_path, interpreter_path=interpreter_path, communication_callback=communication_callback, context=qa_list))

    # Tech lead assistant have tndency to make changes on the main branch: discard these
    discard_all_changes(project_path)
    
    i = 0
    while True:
        branch = os.path.join(start_branch, f'attempt-{i}')
        # Start up a dev agent
        worktree_path = setup_worktree(project_path, branch)
        treemap = create_treemap(worktree_path)
        response, history = await dev_agent.run_agent(max_steps=60, global_goal=goal, codebase_summary=str(current_task), repo_path=worktree_path, interpreter_path=interpreter_path, treemap=treemap, agent_id=agent_id, return_hist=True, communication_callback=communication_callback)

        # Summarize history of the agent
        agent_history_summary = await actions.run_action(action_id='summ', prompt_path='summarizehistory', prompt_format_kwargs={'goal': goal, 'history': f"{history} {response}"}, silent=True)
        if communication_callback:
            await communication_callback(agent_history_summary)

        # History + diff: did agent succeed? -> succeeded = True
        if 'GOAL_ACHIEVED' in agent_history_summary.strip():
            commit_changes(worktree_path, 'commit')
            push_branch(worktree_path,branch)
            create_pull_request('JoshuaSeth', 'AI-Price-Crawler', branch, agent_history_summary)
            break

        improve_task_reasoning = await actions.run_action(action_id='imp', prompt_path='improvetask', prompt_format_kwargs={'goal': goal, 'history': agent_history_summary, 'current_task': current_task}, silent=False)
        if communication_callback:
            await communication_callback(improve_task_reasoning)

        # How update current task prompt what problems encountered and how could it do better?
        current_task = try_splitoff_code_w_fallbacks(improve_task_reasoning, ["```md"], '```')
        i += 1

    

if __name__ == '__main__':
    goal = "Build, run and check logs of the meilisearch adder docker container until it works correctly. dont start interactive sessions but you can always execute commands on the built container. Make incisal changes only. test docker container with building, running and logging until you are sure it works.  You can check logs of a running container with docker docker logs --since=1h 'container_id'. Always run in detached mode so you dno't get blocked. Try to cache the docker builds so they run effecitely, changed steps will automatically rebuild. So don't use `no cache`. You might need to add some print statements to the corresponding python service. The database might still be empty so not much might be hapennig in this service yet."
    project_path = "/Users/sethvanderbijl/PitchAI Code/AFASAsk"
    interpreter_path = "/Users/sethvanderbijl/Library/Caches/pypoetry/virtualenvs/afasask_gzb_webapp-sdaNbJy7-py3.10/bin/python"
    asyncio.run(start_dev_until_succeed(goal))