from contextender.text_item_chooser.item_chooser import choose_item
from contextender.text_item_chooser.prompts import (
    DEFAULT_EXTRA_INSTRUCTIONS,
    FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE,
    IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE,
)


# Simulated LLM function for testing
def get_simulated_llm(llm_context_len: int):
    def simulated_llm(prompt: str):
        if not isinstance(prompt, str):
            raise ValueError("prompt is not a string")
        if len(prompt) > llm_context_len:
            raise ValueError("prompt exceeds maximum prompt length")
        return prompt[:50]

    return simulated_llm


def test_immediate_choose_item():
    context = ["item1", "item2", "item3"]
    llm_context_len = 1 << 30
    task = "Choose an item"
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE.format(task=task))
    result = choose_item(context, simulated_llm, llm_context_len, task)
    assert result == expected


def test_multiple_iterations_choose_item():
    context = ["item1", "item2", "item3"] * 50
    llm_context_len = 1000
    task = "Choose an item"
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(
        FINAL_ITEM_CHOOSE_PROMPT_TEMPLATE_TEMPLATE.format(
            extra_instructions=DEFAULT_EXTRA_INSTRUCTIONS,
            task=task,
        )
    )  # NOTE: approximation
    result = choose_item(context, simulated_llm, llm_context_len, task)
    assert result == expected


def test_choose_item_empty_context():
    context = ""
    llm_context_len = 1 << 30
    task = "Choose an item"
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE.format(task=task))
    result = choose_item(context, simulated_llm, llm_context_len, task)
    assert result == expected
