import random

from typing import Optional, List

class Question:
    """
    Represents a portion of an eval, either a few-shot example with a step-by-step reasoning 
    example or a test question.

    The question is used to generate messages to send to the language model. It does
    not internally store anything about the response, but has helper functions for
    parsing the relevant portion of the response and measuring its correctness.
    """
    def __init__(
            self,
            q: str,
            choices: List[str],
            correct: int = 0,
            reason: Optional[str] = None,
            permute: bool = False,
    ):
        """
        Constructor for question class. The question phrase and the answer phrases are mandatory.
        If this represents a few-shot example, then the coder should provide the correct index
        and the appropriate example reason (e.g. chain of thought reasoning, excluding the very
        last uniform bit,
            ("Answer: %d" % correct_index))

        If we are not dealing with a few-shot example, it is assumed that the first answer is the
        correct one.

        :param q: The question phrase
        :param choices: The answer phrases
        :param correct: The index of the correct answer (defaults to 0)
        :param reason: The reason to the question (given only for a few-shot example)
        :param permute: Whether to permute the choices (defaults to False)
        """

        if len(choices) != 4:
            raise ValueError("There must be exactly four choices")
        elif correct < 0 or correct > 3:
            raise ValueError("The correct index must be between 0 and 3")

        self.q = q
        if permute:
            indices = [0,1,2,3]
            random.shuffle(indices)
            self.choices = [choices[i] for i in indices]
            self.correct_index = indices.index(correct)
        else:
            self.choices = choices
            self.correct_index = correct
        self.reason = reason
 
    @property
    def correct_letter(self) -> str:
        return ["A", "B", "C", "D"][self.correct_index]
    
    @property
    def human(self) -> str:
        """
        The portion of the prompt that 'pretends' to be the human conversant.
        """
        choices = self.choices
        return f"""
{self.q} Please select the correct answer from the following options:
(A) {choices[0]}
(B) {choices[1]}
(C) {choices[2]}
(D) {choices[3]}
""" 
    @property
    def assistant(self) -> str:
        """
        The portion of the prompt that provides the assistant dialog. Only useful
        in few-shot questions, not in test questions.
        """
        if self.reason is None:
            raise ValueError("This is not a few-shot example")
        return f"{self.reason} Answer: {self.correct_letter}"

    def __str__(self) -> str:
        if self.reason:
            return f"""
HUMAN: {self.human}

ASSISTANT: {self.assistant}
"""
        else:
            return f"""
HUMAN: {self.human}

ASSISTANT: """
        
    def choice(self, content: str) -> str:
        """Given a response from the assistant, parse out the letter indicating the choice.
        This function need not be on Question, but we might wish to modify the parser
        in an eval-type-specific way, so here it is.
        """
        answer = content[-2:].strip()
        return answer
    
    def measure(self, content: str) -> int: # should this return float to accommodate other eval types?
        """Just like choice but returns a 1 if correct, and 0 if incorrect."""
        c = self.choice(content)
        if c == self.correct_letter:
            return 1
        elif c in ("A", "B", "C", "D"):
            return 0
        else:
            raise IOError(f"Assistant response ('{content}') was not parseable")