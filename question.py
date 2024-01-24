import random

class Question:
    def __init__(self, q, choices,
                 correct=0,
                 reason=None,
                 permute=False,
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
        :param reason: The reason to the question (defaults to None, which indicates a few-
                         shot example)
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
    def correct_letter(self):
        return ["A", "B", "C", "D"][self.correct_index]
    
    @property
    def human(self):
        choices = self.choices
        return f"""
{self.q} Please select the correct answer from the following options:
(A) {choices[0]}
(B) {choices[1]}
(C) {choices[2]}
(D) {choices[3]}
""" 
    @property
    def assistant(self):
        if self.reason is None:
            raise ValueError("This is not a few-shot example")
        return f"{self.reason} Answer: {self.correct_letter}"

    def __str__(self):
        if self.reason:
            return f"""
HUMAN: {self.human}

ASSISTANT: {self.assistant}
"""
        else:
            return f"""
HUMAN: {self.human}

ASSISTANT: """
        
    def choice(self, content):
        """Given a response from the assistant, parse out the letter indicating the choice."""
        answer = content[-2:].strip()
        return answer
    
    def measure(self, content):
        """Just like choice but returns a 1 if correct, and 0 if incorrect."""
        c = self.choice(content)
        if c == self.correct_letter:
            return 1
        else:
            return 0