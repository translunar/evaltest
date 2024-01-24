# evaltest

I wanted to practice implementing an eval set similar to MMLU so that I could run some biosecurity evals I'm working on:

* [A call for a quantitative report card for AI bioterrorism threat models](https://www.lesswrong.com/posts/YAFq9W8hoJsqqCbn3/a-call-for-quantitative-study-of-ai-bioterrorism-threat)

The current goal is to support ChatGPT and Claude. I don't have the resources to test other LLMs.

The actual biosecurity evals are not in here for security reasons. You should put your own in `data/test.csv`, and the format should be:

```
"question?","correct choice","incorrect 1", "incorrect 2", "incorrect 3"
"What is 1+2?","3","4","-3","0"
```

`data/fewshot.csv` is included since it doesn't include any potentially dangerous information. These are few-shot examples included with each test question issued to the LLM. The format is the same as `data/test.csv`, but adds one field which is the example step-by-step reasoning.

When sending the evals to the model, the choices are shuffled.

## Developers

This project uses a Python virtualenv and assumes it's in the `.venv/` directory.
I haven't included any continuous integration scripts because I don't have the
resources to run these. Before pushing, you should do, at minimum,

    .venv/bin/pytest .
    .venv/bin/mypy .

To run, do

    .venv/bin/python eval.py

# License

Copyright Juno Woods, PhD
2024

MIT license