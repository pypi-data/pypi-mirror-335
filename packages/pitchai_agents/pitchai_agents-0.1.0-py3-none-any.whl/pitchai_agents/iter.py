import asyncio
from agent.history import summarize_history

class IterationStep:
    """
    Container for a single iteration's data.
    """
    def __init__(self, step_idx: int):
        self.step_idx = step_idx

class AgentHistoryIterator:
    """
    Minimal custom asynchronous iterator that:
      - Tracks the step index.
      - Calls `summarize_history` on the accumulated history.
      - Saves the history (here, simply appending a dict for demonstration).
    
    This iterator does nothing besides maintaining history and summarizing it.
    """
    def __init__(self, global_goal: str, max_steps: int, agent_id: str, num_medium_summarized: int, num_unsummarized_final: int):
        self.global_goal = global_goal
        self.max_steps = max_steps
        self.agent_id = agent_id
        self.summarized_history = []  # History is stored as a list
        self.step_idx = 0
        self.num_medium_summarized = num_medium_summarized
        self.num_unsummarized_final = num_unsummarized_final

    def __aiter__(self):
        return self

    async def __anext__(self) -> IterationStep:
        if self.step_idx >= self.max_steps:
            raise StopAsyncIteration

        # Run history summarization
        summarized_history = await summarize_history(
            self.global_goal,
            self.summarized_history,
            num_medium_summarized=self.num_medium_summarized,
            num_unsummarized_final=self.num_unsummarized_final,
            agent_id=self.agent_id
        )

        # Create the iteration step object with current state.
        iteration_step = IterationStep(
            step_idx=self.step_idx
        )

        self.summarized_history = summarized_history

        self.step_idx += 1
        return iteration_step



# Example usage:
async def main():
    iterator = AgentHistoryIterator(global_goal="Analyze the system performance", max_steps=5, agent_id="agent_123")
    async for step in iterator:
        print(f"Step {step.step_idx}:")
        print("Summarized history:", step.summarized_history)
        print("Full history:", step.history)

if __name__ == "__main__":
    asyncio.run(main())
