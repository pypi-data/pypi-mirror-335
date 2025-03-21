from typing import Callable, List, Union

from contextender.config import DEFAULT_MAX_COMPRESS_ITERATIONS
from contextender.contextend_llm_request import iterating_split_llm_request
from contextender.text_item_chooser.prompts import (
    DEFAULT_EXTRA_INSTRUCTIONS,
    FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE,
    FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME,
    IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE,
    IMMEDIATE_SOLVE_PROMPT_TEMPLATE_VARIABLE_NAME,
    ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE,
    ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME,
    ITEM_PREFIX,
    ITEM_SEPARATOR,
)


def list2text(lst: List[str]) -> str:
    """
    Converts a list of strings into a single text string with each item prefixed and separated.

    Args:
        lst (List[str]): The list of strings to convert.

    Returns:
        str: A single string where each item is prefixed and separated by the defined separator.
    """  # noqa: E501
    return ITEM_PREFIX + (ITEM_SEPARATOR + ITEM_PREFIX).join(lst)


def choose_item(
    context: Union[str, List[str]],
    llm: Callable,
    llm_context_len: int,
    task: str,
    item_separator: str = ITEM_SEPARATOR,
    item_prefix: str = ITEM_PREFIX,
    extra_iteration_instructions: str = DEFAULT_EXTRA_INSTRUCTIONS,
    max_iterations: int = DEFAULT_MAX_COMPRESS_ITERATIONS,
) -> str:
    """
    Chooses an item from a given context using an iterative approach with a large language model (LLM).
    In this way, contexts exceeding the LLM context length can also be inputted.

    Args:
        context (Union[str, List[str]]): The input context, either as a single string or a list of strings.
        llm (Callable): A callable that interacts with the language model (LLM).
        llm_context_len (int): The maximum context length supported by the LLM.
        task (str): The task description for choosing an item.
        item_separator (str, optional): Separator used to split items. Defaults to ITEM_SEPARATOR.
        item_prefix (str, optional): Prefix used for each item. Defaults to ITEM_PREFIX.
        extra_iteration_instructions (str, optional): Additional instructions for iterative processing. Defaults to DEFAULT_EXTRA_INSTRUCTIONS.
        max_iterations (int, optional): Maximum number of iterations for processing. Defaults to DEFAULT_MAX_COMPRESS_ITERATIONS.

    Returns:
        str: The final chosen item as a string.
    """  # noqa: E501
    if isinstance(context, list):
        context = list2text(context)
    immediate_solve_prompt_template = IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE.format(
        task=task,
    )
    item_choose_prompt_template = ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE.format(
        extra_instructions=extra_iteration_instructions,
        task=task,
    )
    final_choose_prompt_template = FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE.format(
        task=task,
    )
    return iterating_split_llm_request(
        context,
        llm,
        llm_context_len,
        immediate_solve_prompt_template,
        item_choose_prompt_template,
        item_choose_prompt_template,
        final_choose_prompt_template,
        IMMEDIATE_SOLVE_PROMPT_TEMPLATE_VARIABLE_NAME,
        ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME,
        ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME,
        FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_VARIABLE_NAME,
        item_separator,
        item_prefix,
        item_separator,
        max_iterations,
    )
