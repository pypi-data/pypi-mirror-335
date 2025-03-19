import os
import subprocess
import asyncio
from uuid import uuid4
from chat.ui_msg_actions import UIMsgActions
from agent.agents import simple_dev_agent, tech_lead
from code_ops.treemap import create_treemap
from agent.dynamic_unittest import create_or_update_unittests
from server.task_config import TaskConfig
from agent.questions.codebase_followup_subquestions import n_level_question_research
from guardrails.filepaths import which_filepaths_may_be_edited

# Import the new Git functions from our git.py module
from code_ops.git import (
    clone_repo,
    checkout_branch,
    create_branch_from,
    commit_all_changes,
    push_branch,
    get_diff,
    delete_local_branch,
    sync_repo_with_remote,
    create_pull_request,
    force_commit,
)

# Global parameters
NUM_EVOLUTION_STEPS = 50
NUM_CONCURRENT_AGENTS = 3
STEPS_PER_ITERATION = 6

async def spawn_dev_on_branch(
    clone_path: str,
    branch_name: str,
    base_branch: str,
    communication_callback=None,
    agent_id=uuid4(),
    enriched_task_description=None,
    current_history=[],
    task_config: TaskConfig = None,
    editable_filepaths=None,
    actions=None,
):
    """
    In the given clone (clone_path), create a new branch from base_branch,
    run the agent on that branch, and return its results.
    """
    print('Spawning agent on branch:', branch_name)
    # Create and check out the new branch in the clone
    create_branch_from(clone_path, branch_name, base_branch)
    treemap = create_treemap(clone_path)


    # Run the agent on the new branch (for max_steps=3)
    response, agent_full_history, files_diff_str, summarized_history = await simple_dev_agent.run_agent(
        max_steps=STEPS_PER_ITERATION,
        codebase_summary=str(enriched_task_description),
        repo_path=clone_path,
        treemap=treemap,
        agent_id=agent_id,
        communication_callback=communication_callback,
        current_history=current_history,
        task_config=task_config,
        editable_filepaths=editable_filepaths,
        msg_actions=actions
    )

    return response, summarized_history, agent_full_history, files_diff_str, clone_path, branch_name

    
async def dev_evolution_loop(
    task_config: TaskConfig,
    communication_callback=None,
    queue=None,
    wait_for_user_response=None,
    agent_id=uuid4()
):
    """
    This loop implements our evolution flow using cloned repositories:
      1. At the start, we clone the repository once per agent.
      2. In each round, every agent branches off the current base branch,
         runs for a fixed number of steps, commits & pushes its changes.
      3. We compare each branch (via diffs) and choose the best branch.
      4. Non-chosen branches are deleted and all clones are synced to the best branch.
      5. The next round starts with a branch off the chosen branch.
      
    For the first round, a unique identifier is appended to ensure uniqueness.
    Subsequent rounds simply extend the branch chain.
    """


    msg_actions = UIMsgActions(headless=True)
    enriched_task_description = task_config.goal
    
    # Start by some codebase QA and enriching the task description
    qa_list  = await n_level_question_research(task_config.goal, task_config.project_path, task_config.interpreter_path, communication_callback, msg_actions=msg_actions)
    enriched_task_description = str(await tech_lead.reformulate_enrich_task(goal_or_question=task_config.goal, project_path=task_config.project_path, communication_callback=communication_callback, context=qa_list))

    user_response_to_filepaths = ''
    editable_filepaths = []
    # while user_response_to_filepaths != 'yes':
    #     extra_feedback = ''
    #     if user_response_to_filepaths:
    #         extra_feedback = f"## Previsouly suggested filepaths:\n {editable_filepaths} \n\n ## Feedback of development boss:\n{user_response_to_filepaths}"
    #     editable_filepaths = await which_filepaths_may_be_edited(task_config.goal, task_config.project_path, 
    #                                                        str(qa_list) + str(enriched_task_description), 
    #                                                        extra_prompting=extra_feedback, communication_callback=communication_callback, msg_actions=msg_actions)
    #     print('starting wait for userresponse')
    #     user_response_to_filepaths = await wait_for_user_response(f"Are these good files for the agent to edit? If yes answer 'yes' if not give an explanation how you would like to see it changed.\n\n```python\n{editable_filepaths}\n```", queue)

    NUM_CONCURRENT_AGENTS = task_config.n_agents
    # 1. One-Time Initialization: Clone repo for each agent.
    agent_clones = {}
    for j in range(NUM_CONCURRENT_AGENTS):
        clone_path = os.path.join("/tmp", f"clone_agent_{j}_{uuid4().hex}")
        clone_repo(task_config.remote_url, clone_path)
        checkout_branch(clone_path, task_config.start_branch)
        # Create an initial branch for this agent.
        init_branch = f"agent-{j}"
        create_branch_from(clone_path, init_branch, task_config.start_branch)
        agent_clones[j] = clone_path

    # branch_chain holds the evolving branch name. It starts as the start_branch.
    branch_chain = task_config.start_branch
    # Generate a unique token for the first round only.
    initial_uid = uuid4().hex[:6]
    best_history = []

    for i in range(NUM_EVOLUTION_STEPS):
        current_agents = []
        # For round 0, add the unique token; for later rounds, just append candidate index.
        for j in range(NUM_CONCURRENT_AGENTS):
            clone_path = agent_clones[j]
            if i == 0:
                new_branch = f"{branch_chain}-{initial_uid}-{j}"
            else:
                new_branch = f"{branch_chain}-{j}"
            print(f"Starting agent {j} on branch {new_branch}")
            agent_task = spawn_dev_on_branch(
                clone_path=clone_path,
                branch_name=new_branch,
                base_branch=branch_chain,
                communication_callback=communication_callback,
                agent_id=f"agent_{j}_round_{i}",
                enriched_task_description=enriched_task_description,
                current_history=best_history,
                task_config=task_config,
                editable_filepaths=editable_filepaths,
                actions=msg_actions
            )
            current_agents.append(agent_task)

        # Wait for all agent runs to complete.
        results = await asyncio.gather(*current_agents)

        # 3. Evaluate: For each candidate branch, get a diff against branch_chain.
        diffs = []
        for res in results:
            clone_path = res[4]
            candidate_branch = res[5]
            diff_str = get_diff(clone_path, branch_chain, candidate_branch)
            diffs.append(diff_str)
            # (You might eventually use 'diffs' to choose the best branch automatically)

        # SELECTION
        colleagues_strings = {'goal': task_config.goal, 'colleague_1': '', 'colleague_2': '', 'colleague_3': ''}
        for idx, colleague_result in enumerate(results):
            response, summarized_history, agent_full_history, files_diff_str, clone_path, branch_name = colleague_result
            colleague_string = f"## Colleague {idx}\n\n### Actions taken\n{summarized_history}\n\n### Diff\n{files_diff_str}\n\n---"
            colleagues_strings[f'colleague_{idx}'] = colleague_string
        
        _, args, response = await msg_actions.run_action(prompt_path='closest_to_goal', prompt_format_kwargs=colleagues_strings, return_response=True, model='gemini-2.0-flash-lite')

        if communication_callback:
            await communication_callback(response)

        best_index = args['closest_agent']
        goal_achieved = args['is_goal_reached']
        best_agent = results[best_index]
        best_response_text = best_agent[0]
        best_candidate_branch = best_agent[5]  # e.g. "main-<initial_uid>-1" in round 0, then "chain-1" later.
        best_clone_path = best_agent[4]
        history_summary = best_agent[1]
        best_history = best_agent[2]

        # 4. Commit changes in the best branch and push them.
        # New: Update unit tests on the best branch (using the best clone).
        # if j == 0:
        #     create_or_update_unittests(best_clone_path, task_config.goal, '')
        commit_all_changes(best_clone_path, f"Round {i} commit by best agent")
        push_branch(best_clone_path, best_candidate_branch)

        # Sync all clones: fetch remote, checkout and sync to the best branch.
        for j in range(NUM_CONCURRENT_AGENTS):
            clone_path = agent_clones[j]
            subprocess.run(["git", "fetch", "origin"], cwd=clone_path, check=True)
            force_commit(clone_path)
            checkout_branch(clone_path, best_candidate_branch)
            sync_repo_with_remote(clone_path, best_candidate_branch)

        # Delete non-chosen candidate branches in all clones.
        for j in range(NUM_CONCURRENT_AGENTS):
            clone_path = agent_clones[j]
            if i == 0:
                candidate_branch = f"{branch_chain}-{initial_uid}-{j}"
            else:
                candidate_branch = f"{branch_chain}-{j}"
            if j != best_index:
                delete_local_branch(clone_path, candidate_branch)
            else:
                checkout_branch(clone_path, candidate_branch)

        # After this round, update the branch chain.
        if i == 0:
            branch_chain = f"{branch_chain}-{initial_uid}-{best_index}"
        else:
            branch_chain = f"{branch_chain}-{best_index}"

        # 5. Prepare for next round: all clones should be on the best branch (the new base).
        for j in range(NUM_CONCURRENT_AGENTS):
            clone_path = agent_clones[j]
            force_commit(clone_path)
            checkout_branch(clone_path, best_candidate_branch)
            sync_repo_with_remote(clone_path, best_candidate_branch)

        # Update current_task if desired.
        enriched_task_description = task_config.goal

        # Stop if the goal is achieved.
        if goal_achieved and i > 0:
            for j in range(NUM_CONCURRENT_AGENTS):
                clone_path = agent_clones[j]
                commit_all_changes(clone_path, f"Final commit for {best_candidate_branch}")
                push_branch(clone_path, best_candidate_branch)
            create_pull_request('JoshuaSeth', task_config.remote_url.split('/')[-1].replace('.git', ''),
                                best_candidate_branch, title=best_candidate_branch, body=best_response_text, clone_path=best_clone_path)
            break  # Exit the evolution loop if finished.