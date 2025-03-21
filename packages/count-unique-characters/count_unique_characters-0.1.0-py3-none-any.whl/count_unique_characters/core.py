import argparse
from functools import lru_cache
from collections import Counter


@lru_cache(maxsize=None)
def count_unique_characters(s: str) -> int:
    """
    Counts the number of unique characters in a string.

    Uses caching to optimize repeated calls.

    Args:
        s (str): Input string to parse.

    Returns:
        int: Number of unique characters in the string.

    Raises:
        TypeError: If the input value is not a string.
    """
    if not isinstance(s, str):
        if isinstance(s, (list, set, dict)):
            raise TypeError(f"Unhashable type: '{type(s).__name__}'")
        raise TypeError(f"Input must be a string, but got {type(s).__name__}")

    char_count = Counter(s)
    return sum(1 for count in char_count.values() if count == 1)


def get_input_text():
    """
    Parses command-line arguments and returns the input text.

    Returns:
        str: The input string to be processed.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    parser = argparse.ArgumentParser(
        description="Підрахунок унікальних символів у рядку або файлі"
    )
    parser.add_argument("--string", type=str, help="Рядок для аналізу")
    parser.add_argument("--file", type=str, help="Шлях до текстового файлу")

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Помилка: файл {args.file} не знайдено.")
            exit(1)
    elif args.string:
        return args.string
    else:
        print("Помилка: потрібно передати або --string, або --file.")
        exit(1)


def main():
    """
    The main function of the program that is run when the script is called.
    """
    text = get_input_text()
    result = count_unique_characters(text)
    print(f"Кількість унікальних символів: {result}")


if __name__ == "__main__":
    main()
