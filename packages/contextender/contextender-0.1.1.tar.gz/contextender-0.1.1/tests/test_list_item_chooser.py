import re

import pytest

from contextender.list_item_chooser.item_chooser import choose_item
from contextender.list_item_chooser.prompts import ITEM_CHOOSE_PROMPT_TEMPLATE
from contextender.utils import extract_list


# Simulated LLM function for testing
def get_simulated_llm(max_nr_iteration_items: int, nr_item_choices: int = 2):
    def simulated_llm(prompt: str):
        if not isinstance(prompt, str):
            raise ValueError("prompt is not a string")
        prompt_template = ITEM_CHOOSE_PROMPT_TEMPLATE
        template_lst = extract_list(prompt_template)
        while template_lst is not None:
            prompt_template = prompt_template.replace(str(template_lst), "")
            prompt = prompt.replace(str(template_lst), "")
            template_lst = extract_list(prompt_template)
        lst = extract_list(prompt)
        if len(lst) > max_nr_iteration_items:
            raise ValueError("too many items given to prompt")
        return str(lst[:nr_item_choices])

    return simulated_llm


def test_choose_item_single_iteration_one_item():
    max_nr_items = 1
    items = ["item1"]
    llm = get_simulated_llm(max_nr_items, 1)
    result = choose_item(items, llm, "Choose the item", max_nr_items)
    assert result == "item1"


def test_choose_item_single_iteration_one_item_single_list():
    max_nr_items = 1
    items = ["item1"]
    llm = get_simulated_llm(max_nr_items, 1)
    result = choose_item(
        items, llm, "Choose the item", max_nr_items, single_item_list=True
    )
    assert result == ["item1"]


def test_choose_item_single_iteration_five_item():
    max_nr_items = 5
    nr_item_choices = 2
    items = ["item1", "item2", "item3", "item4", "item5"]
    llm = get_simulated_llm(max_nr_items, nr_item_choices)
    result = choose_item(items, llm, "Choose the item", max_nr_items)
    assert result == items[:nr_item_choices]


def test_choose_item_multiple_iterations():
    max_nr_items = 2
    nr_item_choices = 1
    items = ["item1", "item2"]
    llm = get_simulated_llm(max_nr_items, nr_item_choices)
    result = choose_item(items, llm, "Choose the item", max_nr_items)
    assert result == items[0]


def test_choose_item_empty_list():
    max_nr_items = 1
    items = []
    llm = get_simulated_llm(max_nr_items)
    result = choose_item(items, llm, "Choose the item", max_nr_items)
    assert result == []


def test_choose_item_exceed_max_iterations():
    max_nr_items = 2
    items = ["item"] * 100
    nr_item_choices = 1
    max_iterations = 2
    llm = get_simulated_llm(max_nr_items, nr_item_choices)
    with pytest.raises(
        RuntimeError,
        match=re.escape(f"Exceeded maximum number of iterations ({max_iterations})"),
    ):
        choose_item(
            items, llm, "Choose the item", max_nr_items, max_iterations=max_iterations
        )


def test_choose_item_infinite_loop_detection():
    max_nr_items = 1
    items = ["item1", "item1"]
    llm = get_simulated_llm(max_nr_items)
    with pytest.raises(
        RuntimeError, match="Infinite loop detected during compression."
    ):
        choose_item(items, llm, "Choose the item", max_nr_items)
