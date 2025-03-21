ITEM_CHOOSE_PROMPT_TEMPLATE = """You are an assistant choosing items according to a task.
Choose one or more items according to the task below.
Output the chosen item/items as a Python list (e.g. ['abc', '123'], or [2]).
Output nothing else than the list.

TASK: {task}
ITEMS: {items}
"""  # noqa: E501
TASK_TEMPLATE_VARIABLE = "task"
ITEMS_TEMPLATE_VARIABLE = "items"
