import os
import csv
from openai import OpenAI
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from question import Question

from typing import List, Dict, Sequence

def append_user_messages(
        messages: List[Dict[str,str]],
        fewshot: Sequence[Question],
        test: Question
    ) -> List[Dict[str,str]]:

    for q in fewshot: # Give few-shot examples
        messages.append({"role": "user", "content": q.human})
        messages.append({"role": "assistant", "content": q.assistant})

    # Issue the test question
    messages.append({"role": "user", "content": test.human })

    return messages

def system_message_content() -> str:
    """
    This is in a function because later we might modify the system message functionally.
    """
    return "You are a virologist, microbiologist, and epidemiologist. You should answer questions like an expert in these subjects. Let's think step by step. Finally, write Answer: and the letter of the answer you think is correct. For example, 'Answer: A'"

def openai_complete(
        fewshot: Sequence[Question],
        test: Question,  
        temperature: float = 0.0,
        max_tokens: int = 1024,      
) -> str:
    """
    Handles OpenAI/ChatGPT completion requests.
    """
    messages = [
        { "role": "system",
          "content": system_message_content() },
    ]
    messages = append_user_messages(messages, fewshot, test)

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages, # type:ignore
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if len(response.choices) == 0:
        raise ValueError("GPT returned no choices")
    if response.choices[0].message.content is None:
        raise ValueError("GPT returned no content")

    return response.choices[0].message.content

def anthropic_complete(
        fewshot: Sequence[Question],
        test: Question,
        temperature: float = 0.0,
        max_tokens: int = 1024,
) -> str:
    """
    Handles Anthropic/Claude completion requests.
    """
    messages: List[Dict[str,str]] = []
    append_user_messages(messages, fewshot, test)
    print(messages)

    client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )
    response = client.beta.messages.create(
        model="claude-2.1",
        messages=messages, # type:ignore
        temperature=temperature,
        max_tokens=max_tokens,
        system=system_message_content(),
    )

    return response.content[0].text

def complete(
        fewshot: Sequence[Question],
        test: Question,
        mode: str = "OpenAI",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
    """
    Request a completion for a sequence of few-shot examples and a test question.
    """

    if mode == "OpenAI":
        return openai_complete(fewshot, test, temperature, max_tokens)
    
    elif mode == "Anthropic":
        return anthropic_complete(fewshot, test, temperature, max_tokens)
    
    else:
        raise ValueError(f"Expected mode OpenAI or Anthropic, got {mode}")

def choice(
        fewshot: Sequence[Question],
        test: Question,
        mode: str = "OpenAI",
    ) -> str:
    """
    Parse out the choice from the response to the test question (given some set of
    few-shot examples to make sure the choice is in a parsable format).
    """
    content = complete(fewshot, test, mode=mode)
    answer = test.choice(content)
    return answer

def measure(
        fewshot: Sequence[Question],
        test: Question,
        mode: str = "OpenAI",
    ) -> int:
    """
    Requests a completion and determines whether the response matches the expected
    result. Returns some value between 0 and 1 inclusive, in theory. In practice,
    returns exactly 0 or exactly 1 for this type of eval.
    """
    content = complete(fewshot, test, mode=mode)
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
        count_correct += measure(fewshot_qa, test_q, "Anthropic")
        count_total += 1

    print("Accuracy: %d/%d = %f" % (count_correct, count_total, count_correct/count_total))




