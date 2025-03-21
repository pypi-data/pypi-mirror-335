from typing import Callable, List

from contextender.config import DEFAULT_MAX_COMPRESS_ITERATIONS
from contextender.utils import max_tv_values_len, text_splitter


def split_llm_request(
    llm: Callable,
    llm_context_len: int,
    prompt_template: str,
    text_template_variable_name: str,
    text: str,
    text_separator: str,
) -> List[str]:
    """
    Splits a text into smaller parts and processes each part with a language model (LLM).

    Args:
        llm (Callable): A callable that interacts with the language model.
        llm_context_len (int): The maximum context length supported by the LLM.
        prompt_template (str): The template for the prompt to be sent to the LLM.
        text_template_variable_name (str): The variable name in the template to be replaced with text parts.
        text (str): The input text to be split and processed.
        text_separator (str): The separator used to split the text.

    Returns:
        List[str]: A list of responses from the LLM for each text part.
    """  # noqa: E501
    max_text_part_len = max_tv_values_len(
        prompt_template,
        [text_template_variable_name],
        llm_context_len,
    )
    if max_text_part_len <= 0:
        raise ValueError("prompt_template is bigger than llm_context_len")
    llm_answers = []
    for text_part in text_splitter(text, max_text_part_len, text_separator):
        prompt = prompt_template.format(**{text_template_variable_name: text_part})
        llm_answer = llm(prompt)
        llm_answers.append(llm_answer)
    return llm_answers


def split_join_llm_request(
    llm: Callable,
    llm_context_len: int,
    prompt_template: str,
    text_template_variable_name: str,
    text: str,
    text_separator: str,
    post_process: Callable,
    separator: str,
) -> str:
    """
    Splits a text, processes each part with a language model (LLM), post-processes the results, and joins them.

    Args:
        llm (Callable): A callable that interacts with the language model.
        llm_context_len (int): The maximum context length supported by the LLM.
        prompt_template (str): The template for the prompt to be sent to the LLM.
        text_template_variable_name (str): The variable name in the template to be replaced with text parts.
        text (str): The input text to be split and processed.
        text_separator (str): The separator used to split the text.
        post_process (Callable): A callable to post-process each LLM response.
        separator (str): The separator used to join the post-processed responses.

    Returns:
        str: The joined result of post-processed LLM responses.
    """  # noqa: E501
    llm_answers = split_llm_request(
        llm,
        llm_context_len,
        prompt_template,
        text_template_variable_name,
        text,
        text_separator,
    )
    post_processed_answers = [post_process(ans) for ans in llm_answers]
    return separator.join(post_processed_answers)


def iterating_split_llm_request(
    text: str,
    llm: Callable,
    llm_context_len: int,
    immediate_solve_prompt_template: str,
    init_compress_prompt_template: str,
    compress_compression_prompt_template: str,
    final_task_prompt_template: str,
    immediate_text_template_variable_name: str = "text",
    init_text_template_variable_name: str = "text",
    compressions_template_variable_name: str = "compressions",
    final_compressions_template_variable_name: str = "compressions",
    text_separator: str = " ",
    compression_item_prefix: str = "NEW ITEM:\n",
    compression_items_separator: str = "\n\n",
    max_iterations: int = DEFAULT_MAX_COMPRESS_ITERATIONS,
) -> str:
    """
    Iteratively processes a text using a language model (LLM) to handle large inputs.

    Args:
        text (str): The input text to be processed.
        llm (Callable): A callable that interacts with the language model.
        llm_context_len (int): The maximum context length supported by the LLM.
        immediate_solve_prompt_template (str): Template for the immediate solve prompt.
        init_compress_prompt_template (str): Template for the initial compression prompt.
        compress_compression_prompt_template (str): Template for compressing intermediate results.
        final_task_prompt_template (str): Template for the final task prompt.
        immediate_text_template_variable_name (str, optional): Variable name for the immediate solve text. Defaults to "text".
        init_text_template_variable_name (str, optional): Variable name for the initial compression text. Defaults to "text".
        compressions_template_variable_name (str, optional): Variable name for intermediate compressions. Defaults to "compressions".
        final_compressions_template_variable_name (str, optional): Variable name for final compressions. Defaults to "compressions".
        text_separator (str, optional): Separator used to split the text. Defaults to " ".
        compression_item_prefix (str, optional): Prefix for each compression item. Defaults to "NEW ITEM:\n".
        compression_items_separator (str, optional): Separator for compression items. Defaults to "\n\n".
        max_iterations (int, optional): Maximum number of iterations for compression. Defaults to DEFAULT_MAX_COMPRESS_ITERATIONS.

    Returns:
        str: The final processed result from the LLM.

    Raises:
        RuntimeError: If the maximum number of iterations is reached or an infinite loop is detected.
    """  # noqa: E501
    # Try to solve task with one single prompt
    immediate_solve_prompt = immediate_solve_prompt_template.format(
        **{immediate_text_template_variable_name: text}
    )
    if len(immediate_solve_prompt) <= llm_context_len:
        return llm(immediate_solve_prompt)

    # Initial compression
    compressions_str = split_join_llm_request(
        llm,
        llm_context_len,
        init_compress_prompt_template,
        init_text_template_variable_name,
        text,
        text_separator,
        lambda s: compression_item_prefix + s,
        compression_items_separator,
    )

    # Compress compressions until it is possible to render final_task_prompt
    max_final_compressions_len = max_tv_values_len(
        final_task_prompt_template,
        [final_compressions_template_variable_name],
        llm_context_len,
    )
    count_iterations = 1
    while len(compressions_str) > max_final_compressions_len:
        if count_iterations > max_iterations:
            raise RuntimeError("Maximum iterations reached during compression.")
        new_compressions_str = split_join_llm_request(
            llm,
            llm_context_len,
            compress_compression_prompt_template,
            compressions_template_variable_name,
            compressions_str,
            compression_item_prefix,
            lambda s: compression_item_prefix + s,
            compression_items_separator,
        )
        if len(new_compressions_str) >= len(compressions_str):
            raise RuntimeError("Infinite loop detected during compression.")
        compressions_str = new_compressions_str
        count_iterations += 1

    # Solve task
    final_prompt = final_task_prompt_template.format(
        **{final_compressions_template_variable_name: compressions_str}
    )
    final_answer = llm(final_prompt)
    return final_answer
