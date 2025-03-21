from contextender.utils import text_splitter


def test_no_separator():
    text = "This is a sample text for testing."
    max_chars = 10
    expected = ["This is a ", "sample tex", "t for test", "ing."]
    result = list(text_splitter(text, max_chars))
    assert result == expected


def test_with_separator():
    text = "This is a sample text for testing."
    max_chars = 10
    separator = " "
    expected = ["This is a", " sample", " text for", " testing."]
    result = list(text_splitter(text, max_chars, separator))
    assert result == expected


def test_long_word():
    text = "Thisisaverylongwordthatneedstobesplit."
    max_chars = 10
    expected = ["Thisisaver", "ylongwordt", "hatneedsto", "besplit."]
    result = list(text_splitter(text, max_chars))
    assert result == expected


def test_empty_text():
    text = ""
    max_chars = 10
    expected = []
    result = list(text_splitter(text, max_chars))
    assert result == expected


def test_separator_longer_than_max_chars():
    text = "This is just some sample text for testing."
    max_chars = 5
    separator = "sample"
    expected = [
        "This ",
        "is ju",
        "st so",
        "me ",
        "sampl",
        "e tex",
        "t for",
        " test",
        "ing.",
    ]
    result = list(text_splitter(text, max_chars, separator))
    assert result == expected
