IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE = """Given the list of items below, solve the task below.

ITEMS:
{{items}}

TASK:
{task}
"""  # noqa: E501
IMMEDIATE_SOLVE_PROMPT_TEMPLATE_VARIABLE_NAME = "items"


ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE = """You are an assistant choosing items from a list according to a task.
The full list has been split up into several smaller list.
Given one of these partial list below, choose the items most relevant for solving the task below.
The chosen items will proceed for a final selection together with chosen relevant items from the other partial lists.
Output nothing else than a list of the chosen items on the same format as the list below.
Other instructions: {extra_instructions}

PARTIAL ITEM LIST:
{{items}}

TASK:
{task}
"""  # noqa: E501
ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME = "items"


FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE = """You are an assistant choosing items from a list according to a task.
Given the item list below, summaries of a longer text below, solve the task below.

ITEM LIST:
{{items}}

TASK:
{task}
"""  # noqa: E501
FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME = "items"

DEFAULT_EXTRA_INSTRUCTIONS = "-"

ITEM_PREFIX = "ITEM:\n"
ITEM_SEPARATOR = "\n\n"
