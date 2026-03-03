from core.llm import ClaudeLLM
from core.prompts import PLANNER_PROMPT

class PlannerAgent:
    def __init__(self):
        self.llm = ClaudeLLM()

    def plan(self, question: str, context: str = "") -> str:
        prompt = PLANNER_PROMPT.format(
            question=question,
            context=context if context else "No additional context provided."
        )
        return self.llm.generate(prompt)
