from code_ops.splitoff import try_splitoff_code_w_fallbacks
from code_ops.unittest_ops import run_pytest

def complete_analysis(final_answer: str) -> str:
    """
    A function the agent can call to stop the process and give back the final summary.
    """
    globals()['final_answer'] = final_answer

    final_answer_str = f"""
```finalanswermarkdown
{final_answer}
```
"""
    print(final_answer_str)

    return final_answer_str





def stop_if_allowed(code_str: str, logs: str, current_history: list, repo_path: str, interpreter_path: str, step_idx, max_steps, additional_return_values:tuple=None):
    '''Check whether we WANT to stop and MAY stop.'''
    # RETURN VALUE
    res = try_splitoff_code_w_fallbacks(logs, ["```finalanswermarkdown"]) + f"\n\n{current_history[-1]['thought']}"
    return_values = res
    if additional_return_values:
        return_values = (res,) + additional_return_values

    # MAX STEPS REACHED
    if step_idx > max_steps:
        return True, return_values

    # NO STOP WANTED
    if not 'complete_analysis(' in code_str:
        return False, None
    
    # STOP WANTED, PYTEST FAIL
    succes, test_results = run_pytest(repo_path, interpreter_path, return_success_state=True)
    if not succes:
        logs += f"# ERROR\n\n The tests did not pass, you are not allowed to finish. Only once ALL unit tests pass are you allowed to finalize and wrap up.\n\n ##Test results:\n\n {test_results}"
        return False, None

    # STOP WANTED, ALLOWED        
    return True, return_values