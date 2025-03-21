import ast
import re
import warnings
from functools import reduce
from typing import Callable, Generator, List, Optional


def find_context_len(llm: Callable) -> int:
    """
    Determines the context length supported by the language model (LLM).

    Args:
        llm (Callable): A callable that interacts with the language model.

    Returns:
        int: The maximum context length in characters.
    """
    # TODO: don't hardcode - try prompts of different lengths until failure
    context_len = 20000  # NOTE: 20000 chars corresponds to ~5000 tokens
    return context_len


def max_tv_values_len(
    template_str: str, template_variables: List[str], max_chars: int
) -> int:
    """
    Calculates the maximum length of text that can fit into a template.

    Args:
        template_str (str): The template string.
        template_variables (List[str]): A list of variable names in the template.
        max_chars (int): The maximum number of characters allowed.

    Returns:
        int: The maximum length of text that can fit into the template.
    """  # noqa: E501
    max_len = max_chars - len(template_str)
    for template_variable in template_variables:
        search = f"{{{template_variable}}}"
        max_len += template_str.count(search) * len(search)
    return max_len


def _text_splitter(text: str, max_chars: int) -> Generator[str, None, None]:
    """
    Splits a text into smaller chunks of a specified maximum length.

    Args:
        text (str): The input text to split.
        max_chars (int): The maximum number of characters per chunk.

    Yields:
        str: A chunk of the text.
    """
    start_now = 0
    while start_now < len(text):
        end_now = min(start_now + max_chars, len(text))
        yield text[start_now:end_now]
        start_now = end_now


def text_splitter(
    text: str, max_chars: int, prefix_separator: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Splits a text into smaller chunks, optionally using a prefix separator.

    Args:
        text (str): The input text to split.
        max_chars (int): The maximum number of characters per chunk.
        prefix_separator (Optional[str], optional): A separator to split the text. Defaults to None.

    Yields:
        str: A chunk of the text.

    Raises:
        ValueError: If max_chars is less than or equal to 0.
    """  # noqa: E501
    if max_chars <= 0:
        raise ValueError("max_chars must be greater than 0")
    if isinstance(prefix_separator, str) and len(prefix_separator) > 0:
        wo_sep_parts = text.split(prefix_separator)
        text_parts = [prefix_separator + part for part in wo_sep_parts[1:]]
        if not text.startswith(prefix_separator):
            text_parts = [wo_sep_parts[0]] + text_parts
        # TODO: raise warning if too long items
        text_parts = reduce(
            lambda x, y: x + list(_text_splitter(y, max_chars)), text_parts, []
        )  # Split too long items (shouldn't be any if separator well chosen)
        if len(text_parts) > 1:
            warnings.warn(
                "Couldn't find a good index to split without exceeding context length. Try choosing a better separator."  # noqa: E501
            )
        sb = []
        sb_acc_len = 0
        for text_part in text_parts:
            if sb_acc_len + len(text_part) <= max_chars:
                sb.append(text_part)
                sb_acc_len += len(text_part)
            else:
                yield "".join(sb)
                sb = [text_part]
                sb_acc_len = len(text_part)
        yield "".join(sb)
    else:
        for text_part in _text_splitter(text, max_chars):
            yield text_part


def extract_list(llm_response: str) -> Optional[List]:
    """
    Extracts the first list found in a string response from the language model.

    Args:
        llm_response (str): The response string from the language model.

    Returns:
        Optional[List]: The extracted list, or None if no valid list is found.
    """
    match = re.search(
        r"\[.*?\]", llm_response, re.DOTALL
    )  # Extracts the first [...] found
    if match:
        try:
            return ast.literal_eval(match.group(0))
        except (SyntaxError, ValueError):
            pass
    return None  # Return None if no valid list is found
