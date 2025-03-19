def time_almost_up_warning(step_idx:int, max_steps:int) -> str:
    '''Returns a warning message if the time is almost up. If not close to final step, returns an empty string.'''
    if step_idx == max_steps-2:
            return "\n\nAt this point you have one step left. Make sure to wrap up here and give the best advice you got. You can take 1 more step so use it wisely and do not waste it on detailed reesearch. Just 1 global thing you can still research before you'll have to answer. So think about you want to do, the only thing you can do before returning your final answer."

    if step_idx == max_steps:
        return '\n\nAt this point you have used up ALL your time and steps. So the previous advice is overriden. You MUST finish now. You must call complete_analysis in your code now, not later. You must wrap up the process.'
    
    return ''