import os
import csv
from openai import OpenAI

from question import Question

def prepare_messages(fewshot, test):
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
        fewshot,
        test,
        practice=False
    ):
    messages = prepare_messages(fewshot, test)

    if practice:
        return messages
    else:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )

        return response.choices[0].message.content

def choice(fewshot, test):
    content = complete(fewshot, test)
    answer = test.choice(content)
    return answer

def measure(fewshot, test):
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




