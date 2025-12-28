from dialogue.llm.deepseek import DeepSeekClient
from dialogue.modes import DialogueMode
from pathlib import Path


import os

class DialogueManager:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")

        self.llm = DeepSeekClient(api_key=api_key)

        BASE_DIR = Path(__file__).parent / "prompts"

        self.prompts = {
            DialogueMode.explain: (BASE_DIR / "explain.txt").read_text(),
            DialogueMode.quiz: (BASE_DIR / "quiz.txt").read_text(),
            DialogueMode.review: (BASE_DIR / "review.txt").read_text(),
        }


    def handle(self, mode: DialogueMode, question: str) -> str:
        template = self.prompts.get(mode)

        if template:
            prompt = template.format(question=question)
        else:
            prompt = question

        return self.llm.ask(prompt)