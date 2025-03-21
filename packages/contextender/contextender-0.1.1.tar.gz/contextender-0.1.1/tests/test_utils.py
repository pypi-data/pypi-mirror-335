from contextender.utils import extract_list


def test_extract_list_valid():
    response = "Here is your list: [1, 'hello', 3.14, True]"
    expected = [1, "hello", 3.14, True]
    assert extract_list(response) == expected


def test_extract_list_invalid():
    response = "Here is your list: [1, 'hello', 3.14, True"
    assert extract_list(response) is None


def test_extract_list_no_list():
    response = "Here is your list: no list here"
    assert extract_list(response) is None
