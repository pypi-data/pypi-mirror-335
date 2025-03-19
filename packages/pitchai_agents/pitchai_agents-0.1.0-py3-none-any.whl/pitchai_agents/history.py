from typing import List
from chat.ui_msg_actions import UIMsgActions
from code_ops.splitoff import try_splitoff_code
import json
import os

# Global cache for summarizations
summarization_cache = {}


async def summarize_history(global_goal: str, history: List[dict], num_unsummarized_final: int = 3, num_medium_summarized: int = 3, agent_id = None) -> str:
    """
    Summarizes the history.
    
    The history is a list of dicts representing actions. Dicts can contain any keys. Generally these actions will contain a thought, code and code execution result. The last few steps will remain unsummarized while the first few steps will be heavily summarized.
    """
    # First sanitize the history
    # history = ['\n'.join(f"{key}: value") for step_dict in history for key, value in step_dict.items()]


    if len(history) == 0:
        return []

    msg_actions = UIMsgActions(headless=True)

    # 0. Remove the 'result' key from the history except for the last step
    for step_dict in history[:-1]:
        step_dict.pop('result', None)

    # 1. Split the history into sections
    unsummarized = history[-num_unsummarized_final:]
    history_without_unsummarized = history[:-num_unsummarized_final]
    medium_summarized = history_without_unsummarized[-num_medium_summarized:]
    history_without_medium_summarized = history_without_unsummarized[:-num_medium_summarized]
    hard_summarized = history_without_medium_summarized

    # 2. Summarize the relevant sections
    summarized_early_history = await msg_actions.run_action(
        prompt_path='agentsummarizer',
        prompt_format_kwargs={'content': hard_summarized, 'goal': global_goal},
        model='gemini-2.0-flash-lite'
    )
    summarized_early_history = [try_splitoff_code(summarized_early_history, '```md', '```')]

    summarized_medium_history = []
    for msg in medium_summarized:
        # Check if a cached summary exists for this message
        if str(msg) in summarization_cache:
            medium_hist_msg_summarized = summarization_cache[str(msg)]
        else:
            medium_hist_msg_summarized = await msg_actions.run_action(
                prompt_path='agentsummarizer',
                prompt_format_kwargs={'content': msg, 'goal': global_goal},
                model='gemini-2.0-flash-lite'
            )
            medium_hist_msg_summarized = try_splitoff_code(medium_hist_msg_summarized, '```md', '```')
            # Cache the summary for later use
            summarization_cache[str(msg)] = medium_hist_msg_summarized

        summarized_medium_history.append(medium_hist_msg_summarized)

    # Late history is not summarized
    summarized_late_history = []
    for msg in unsummarized:
        summarized_late_history.append(msg)
    


    # 3. Combine the sections
    full_summary = summarized_early_history + summarized_medium_history + summarized_late_history

    os.makedirs(os.path.dirname(f'afasask/agent/summarizations/summarized_history_{agent_id}.json'), exist_ok=True)
    with open(f'afasask/agent/summarizations/summarized_history_{agent_id}.json', 'w') as f:
        # Ensure path exists
        json.dump(full_summary, f, indent=4)

    return full_summary
