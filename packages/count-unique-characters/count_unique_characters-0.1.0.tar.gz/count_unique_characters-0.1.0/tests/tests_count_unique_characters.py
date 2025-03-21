import timeit
import pytest
from unittest.mock import patch, mock_open
from src.count_unique_characters.core import count_unique_characters, get_input_text

# Тести для функції count_unique_characters


@pytest.mark.parametrize("input_string, expected", [
    ("abbbccdf", 3),  # 'a', 'd', 'f' зустрічаються один раз
    ("aaaaa", 0),  # Немає символів, що зустрічаються один раз
    ("abcdef", 6),  # Всі символи зустрічаються один раз
    ("", 0),  # Порожній рядок
    ("aabbccde", 2),  # 'd' і 'e' зустрічаються один раз
    ("abcabc", 0),  # Немає унікальних символів
])
def test_count_unique_characters(input_string, expected):
    """
    We test the function count_unique_characters with valid string input.
    The correctness of the unique character count is checked.
    """
    assert count_unique_characters(input_string) == expected


@pytest.mark.parametrize("invalid_input",
                         [123, 3.14, True, None, [], {}, set()])
def test_count_unique_characters_invalid_input(invalid_input):
    """
    We test the behavior of the count_unique_characters function when invalid input is given.
    We expect a TypeError to occur.
    """
    with pytest.raises(TypeError) as exc_info:
        count_unique_characters(invalid_input)

    # Перевірка на наявність повідомлення про тип
    exc_message = str(exc_info.value)
    if isinstance(invalid_input, (list, dict, set)):
        # Для незмірних типів перевіряємо їх детальні повідомлення
        assert f"unhashable type: '{
            type(invalid_input).__name__}'" in exc_message
    else:
        # Для інших типів вводимо стандартне повідомлення
        assert 'Input must be a string' in exc_message


# Фікстура для мокування sys.argv
@pytest.fixture
def mock_args():
    with patch("sys.argv", ["collection_network.py", "--string", "test string"]):
        yield


# Тести для мокування файлу та аргументів
@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_get_input_text_with_file(mock_file):
    """
    We test getting text from a file.
    """
    with patch("sys.argv", ["collection_network.py", "--file", "fake_path"]):
        result = get_input_text()
        assert result == "file content"
        mock_file.assert_called_once_with("fake_path", "r", encoding="utf-8")


@pytest.mark.usefixtures("mock_args")
def test_get_input_text_with_string():
    """
    We test getting text from a string
    """
    result = get_input_text()
    assert result == "test string"


@patch("builtins.open", new_callable=mock_open, read_data="file content")
def test_get_input_text_with_both_params(mock_file):
    """
    We test the situation when both a string and a file are passed.
    The value from the file should be used, since the --file parameter has higher precedence.
    """
    with patch("sys.argv", ["collection_network.py", "--string", "test string", "--file", "fake_path"]):
        result = get_input_text()
        assert result == "file content"
        mock_file.assert_called_once_with("fake_path", "r", encoding="utf-8")


# Тести для кешування
@pytest.mark.parametrize(
    "test_string",
    [
        "shortstring",
        "longstringwithmanycharacters" * 10,
        "anotherlongstring" * 5
    ]
)
def test_cache_functionality(test_string):
    """
    We test whether caching works with lru_cache for different input strings.
    We check whether the result is cached and the number of calculations is reduced.
    """
    count_unique_characters.cache_clear()  # Очищуємо кеш перед тестом

    first_call_time = timeit.timeit(
        lambda: count_unique_characters(test_string),
        number=5) / 5
    second_call_time = timeit.timeit(
        lambda: count_unique_characters(test_string), number=1)

    # Дозволяємо трохи більше гнучкості, оскільки кешування в lru_cache може
    # відрізнятися
    assert second_call_time < first_call_time * 0.75


@pytest.mark.parametrize(
    "test_string, expected_hits, expected_misses",
    [
        ("abcde", 1, 1),  # Перший виклик - промах, другий - хіт
        ("longstringwithmanycharacters" * 10, 1, 1),
        ("abcde", 1, 1),  # 1 промах, 1 хіт після одного виклику
    ],
)
def test_cache_info(test_string, expected_hits, expected_misses):
    """
    Testing cache information
    """
    count_unique_characters.cache_clear()  # Очищуємо кеш перед тестом

    count_unique_characters(test_string)  # Перший виклик (міс)
    count_unique_characters(test_string)  # Другий виклик (хіт)

    cache_info = count_unique_characters.cache_info()

    assert cache_info.hits == expected_hits
    assert cache_info.misses == expected_misses
