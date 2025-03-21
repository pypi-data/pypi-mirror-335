DEFAULT_TASK = "Summarize this text."

IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE = """Given the text below, solve the task below.

TEXT:
{{text}}

TASK:
{task}
"""  # noqa: E501
IMMEDIATE_SOLVE_PROMPT_TEMPLATE_VARIABLE_NAME = "text"


SUMMARIZE_PROMPT_TEMPLATE_TEMPLATE = """You are an assistant summarizing texts.
Summarize the text below as good as you can (it is a part of a larger text and may have been cut of in the middle of a sentence).
Output nothing else than the summary.
Constraints: {constraints}
Other instructions: {extra_instructions}

TEXT TO SUMMARIZE:
{{text}}
"""  # noqa: E501
SUMMARIZE_PROMPT_TEMPLATE_VARIABLE_NAME = "text"


SUMMARIZE_SUMMARIES_PROMPT_TEMPLATE_TEMPLATE = """You are an assistant summarizing texts.
Given the summaries of different parts of a larger text below, write an overall summary of the whole text.
Summaries from some parts of the larger text might be missing, but still write the summary of the whole text as good as you can.
Output nothing else than the summary.
Constraints: {constraints}
Other instructions: {extra_instructions}

SUMMARIES TO SUMMARIZE:
{{summaries}}
"""  # noqa: E501
SUMMARIZE_SUMMARIES_TEMPLATE_VARIABLE_NAME = "summaries"


FINAL_SUMMARY_PROMPT_TEMPLATE_TEMPLATE = """You are an assistant answering to questions and solving tasks.
Given the summaries of a longer text below, solve the task below.

SUMMARIES:
{{summaries}}

TASK:
{task}
"""  # noqa: E501
FINAL_SUMMARY_PROMPT_TEMPLATE_VARIABLE_NAME = "summaries"

DEFAULT_SUMMARY_CONSTRAINTS = (
    "The summary should be one paragraph and at most five sentences."
)
TASK2EXTRA_INSTRUCTIONS = "Write the summary bearing in mind that this question/task is to be answered/solved from the summary: '{task}'"  # noqa: E501


SUMMARY_ITEM_PREFIX = "Summary:\n"
SUMMARY_ITEMS_SEPARATOR = "\n\n"

DEFAULT_TEXT_SEPARATOR = " "
