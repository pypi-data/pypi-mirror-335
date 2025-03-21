from contextender.summarizer.prompts import (
    DEFAULT_TASK,
    FINAL_SUMMARY_PROMPT_TEMPLATE_TEMPLATE,
    IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE,
)
from contextender.summarizer.summarizer import summarize


# Simulated LLM function for testing
def get_simulated_llm(llm_context_len: int):
    def simulated_llm(prompt: str):
        if not isinstance(prompt, str):
            raise ValueError("prompt is not a string")
        if len(prompt) > llm_context_len:
            raise ValueError("prompt exceeds maximum prompt length")
        return prompt[:50]

    return simulated_llm


def test_immediate_summarize():
    text = "a" * 50
    llm_context_len = 1 << 30
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(
        IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE.format(
            task=DEFAULT_TASK,
        ).format(text=text)
    )
    result = summarize(text, simulated_llm, llm_context_len)
    assert result == expected


def test_1_iteration_summarize():
    text = "This is a sample text for testing the summarize function." * 12
    llm_context_len = 700
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(
        FINAL_SUMMARY_PROMPT_TEMPLATE_TEMPLATE
    )  # NOTE: approximation
    result = summarize(text, simulated_llm, llm_context_len)
    assert result == expected


def test_2_iteration_summarize():
    text = "This is a sample text for testing the summarize function." * 50
    llm_context_len = 700
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(
        FINAL_SUMMARY_PROMPT_TEMPLATE_TEMPLATE
    )  # NOTE: approximation
    result = summarize(text, simulated_llm, llm_context_len)
    assert result == expected


def test_summarize_empty_text():
    text = ""
    llm_context_len = 1 << 30
    simulated_llm = get_simulated_llm(llm_context_len)
    expected = simulated_llm(
        IMMEDIATE_SOLVE_PROMPT_TEMPLATE_TEMPLATE.format(task=DEFAULT_TASK).format(
            text=text
        )
    )
    result = summarize(text, simulated_llm, llm_context_len)
    assert result == expected
