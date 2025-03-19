from agent.agents import codebase_answer_agent
import asyncio
from chat.ui_msg_actions import UIMsgActions
from uuid import uuid4
import json
from typing import List
from rich.logging import RichHandler
import logging
from code_ops.treemap import create_treemap
from code_ops.git_ops import discard_all_changes


async def n_level_question_research(
    goal_or_question,
    project_path,
    interpreter_path,
    communication_callback,
    msg_actions=None,
    num_followups: int = 1
) -> List[dict]:
    """
    Generates questions and answers about the codebase in multiple passes. So initial questions are asked. In the second pass follow-up questions are asked based on the newly found information, etc. Essentially a loop around codebaseanswer_agent.

    1) Pass zero: Generate and answer 'initial' questions based on sys_argv_goal.
    2) Passes 1..N: Generate and answer follow-up questions based on the newly acquired Q&A context.

    Returns a concatenated list of {'question': str, 'response': str} dicts.
    """

    concatenated_qa = []
    treemap = create_treemap(project_path)

    # Create default msg_actions if none provided
    if not msg_actions:
        msg_actions = await UIMsgActions.create(headless=True)
    
    # We have 1 initial pass + as many follow-ups as requested
    total_rounds = num_followups + 1

    for round_index in range(total_rounds):
        if round_index == 0:
            # --- PASS #0: INITIAL QUESTIONS ---
            prompt_task = goal_or_question
        else:
            # --- PASS #i: FOLLOW-UP QUESTIONS ---
            prompt_task = (
                f"Ask follow up questions based on what you already know to achieve: {goal_or_question}"
            )

        # 1) Generate N questions
        _, tool_args = await msg_actions.run_action(
            prompt_path='codequestions',
            prompt_format_kwargs={
                'task': prompt_task,
                'context': concatenated_qa,
                'treemap': json.dumps(treemap, indent=2)
            })
        
        async def agent_task(question):
            res = await codebase_answer_agent.run_agent(
                max_steps=8,
                min_steps=3,
                question=question,
                treemap=treemap,
                repo_path=project_path,
                interpreter_path=interpreter_path,
                # communication_callback=communication_callback, Let's not pass a communication callback, to avoid spamming the user
                agent_id=uuid4()
            )

            if communication_callback:
                await communication_callback(f"**Question**\n{question}")
                await communication_callback(f"**Answer**\n{res}")

            return res



        # 2) Spawn tasks to answer each question
        questions = tool_args['questions_list']
        tasks = []
        for question in questions:
            task = agent_task(question)
            tasks.append(task)

        # 3) Collect answers
        dev_responses = await asyncio.gather(*tasks)

        # 4) Pair question with response
        new_qa_pairs = [
            {'question': q, 'response': r}
            for q, r in zip(questions, dev_responses)
        ]



        # 6) Update the concatenated Q&A so it can inform the next pass
        concatenated_qa += new_qa_pairs

        # Not elegant but codebase answer agents sometimes change codebase
        discard_all_changes(project_path)

    return concatenated_qa




if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    async def comm(msg):
        print(msg)

    project_path = "/Users/sethvanderbijl/PitchAI Code/AI Price Crawler"
    interpreter_path = "/Users/sethvanderbijl/Library/Caches/pypoetry/virtualenvs/ai_price_crawler-6CKRPcSL-py3.11/bin/python"
    
    goal = '''please check that the meilisearch adder script works correctly.'''
    output_summary = asyncio.run(n_level_question_research(goal, project_path, interpreter_path, communication_callback=comm, num_followups=3))

    print(json.dumps(output_summary, indent=2))