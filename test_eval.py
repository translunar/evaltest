import unittest

from question import Question

class TestEval(unittest.TestCase):

    def test_permuted_question(self) -> None:
        q = Question("Which of these answers is 1?",
                     ["0+1", "2+0", "3-1", "-1"],
                     reason="2+0 is 2. 0+1 is 1. 3-1 is 2.",
                     permute=True,
        )

        self.assertIn(q.correct_letter, ["A", "B", "C", "D"])
        h = q.human
        a = q.assistant

        self.assertEqual(q.correct_index, q.choices.index("0+1"))
        
        
    def test_unpermuted_question(self) -> None:
        q = Question("Which of these answers is 1?",
                     ["5/0", "1/5", "5/5", "-5/5"],
                     correct=2,
                     permute=False
        )

        self.assertEqual(q.correct_letter, "C")
        h = q.human
        with self.assertRaises(ValueError):
            a = q.assistant

        content = "Some chain of thought reason. Answer: C"
        c = q.choice(content)
        self.assertEqual(c, "C")
        self.assertEqual(c, q.correct_letter)
        self.assertEqual(q.measure(content), 1)

        content = "Some other chain of thought. Answer: A"
        self.assertEqual(q.measure(content), 0)

    def test_permuted_question_with_nonzero_correct(self) -> None:
        choices = ["5/0", "1/5", "5/5", "-5/5"]

        count = 0
        for i in range(10):
            q = Question("Which of these answers is 1?",
                        choices,
                        correct=2,
                        permute=True
            )
            self.assertEqual(q.choices[q.correct_index], choices[2])

