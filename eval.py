import os
import csv
from openai import OpenAI

from question import Question

from typing import List, Dict, Sequence

def prepare_messages(
        fewshot: Sequence[Question],
        test: Question
    ) -> List[Dict[str,str]]:
    """
    Assemble the messages to send to the language model based on a sequence of
    few-shot examples and a single test question.
    """
    
    messages = [
        { "role": "system",
          "content": "You are a virologist, microbiologist, and epidemiologist. You should answer questions like an expert in these subjects. Let's think step by step. Finally, write Answer: and the letter of the answer you think is correct. For example, 'Answer: A'" },
    ]

    for q in fewshot: # Give few-shot examples
        messages.append({"role": "user", "content": q.human})
        messages.append({"role": "assistant", "content": q.assistant})

    # Issue the test question
    messages.append({"role": "user", "content": test.human })

    return messages

def complete(
        fewshot: Sequence[Question],
        test: Question
    ) -> str:
    """
    Request a completion for a sequence of few-shot examples and a test question.
    """
    messages = prepare_messages(fewshot, test)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages, # type:ignore
    )
    if len(response.choices) == 0:
        raise ValueError("GPT returned no choices")
    if response.choices[0].message.content is None:
        raise ValueError("GPT returned no content")

    return response.choices[0].message.content

def choice(
        fewshot: Sequence[Question],
        test: Question
    ) -> str:
    """
    Parse out the choice from the response to the test question (given some set of
    few-shot examples to make sure the choice is in a parsable format).
    """
    content = complete(fewshot, test)
    answer = test.choice(content)
    return answer

def measure(
        fewshot: Sequence[Question],
        test: Question
    ) -> int:
    """
    Requests a completion and determines whether the response matches the expected
    result. Returns some value between 0 and 1 inclusive, in theory. In practice,
    returns exactly 0 or exactly 1 for this type of eval.
    """
    content = complete(fewshot, test)
    print(content)
    return test.measure(content)

if __name__ == "__main__":
    fewshot_qa = []
    fewshot_text = ""
    test_qa = []

    with open("data/fewshot.csv", "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            q = Question(row[0], row[1:5], reason=row[5], permute=True)
            fewshot_qa.append(q)
            fewshot_text += str(q)

    with open("data/test.csv", "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            q = Question(row[0], row[1:5], permute=True)
            test_qa.append(q)

    count_correct = 0
    count_total = 0
    #test_q = test_qa[0]
    #msg = complete(fewshot_qa, test_q, practice=True)
    for test_q in test_qa:
        count_correct += measure(fewshot_qa, test_q)
        count_total += 1

    print("Accuracy: %d/%d = %f" % (count_correct, count_total, count_correct/count_total))




