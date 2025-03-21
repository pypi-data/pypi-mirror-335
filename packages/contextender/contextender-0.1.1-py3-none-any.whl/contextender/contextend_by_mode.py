from typing import Callable, List, Union

from contextender.config import ITEM_CHOOSE_TASK_MODE, SUMMARY_TASK_MODE
from contextender.summarizer.summarizer import summarize
from contextender.text_item_chooser.item_chooser import choose_item
from contextender.utils import find_context_len


def contextend(
    llm: Callable,
    context: Union[str, List[str]],
    task_mode: str = SUMMARY_TASK_MODE,
    task: str = None,
    llm_context_len: int = None,
) -> str:
    """
    Processes the given context using a specified task mode and a language model (LLM).
    The context could be a text (str), or a list of strings, and may exceed the LLM context length.

    Args:
        llm (Callable): The language model function to be used for processing. Takes prompt (str) as input and outputs answer (str).
        context (Union[str, List[str]]): The input context to process. Can be a string or a list of strings.
        task_mode (str, optional): The mode of the task to perform. Defaults to SUMMARY_TASK_MODE.
            - 'summary' (SUMMARY_TASK_MODE): Summarizes the given context.
            - 'item-choose' (ITEM_CHOOSE_TASK_MODE): Chooses an item based on the given context.
        task (str, optional): Additional task-specific instructions or details. Defaults to None.
        llm_context_len (int, optional): The maximum context length supported by the LLM. If None, it will be determined automatically.

    Returns:
        str: The result of processing the context based on the specified task mode.

    Raises:
        ValueError: If an unknown task_mode is provided.
    """  # noqa: E501
    if llm_context_len is None:
        llm_context_len = find_context_len(llm)
    if task_mode == SUMMARY_TASK_MODE:
        return summarize(context, llm, llm_context_len, task)
    elif task_mode == ITEM_CHOOSE_TASK_MODE:
        return choose_item(context, llm, llm_context_len, task)
    else:
        raise ValueError(
            f"Unknown task_mode: {task_mode}. Expected one of: {SUMMARY_TASK_MODE}, {ITEM_CHOOSE_TASK_MODE}."  # noqa: E501
        )
