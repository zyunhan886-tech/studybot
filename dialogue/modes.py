from enum import Enum

class DialogueMode(str, Enum):
    explain = "explain"
    quiz = "quiz"
    review = "review"
