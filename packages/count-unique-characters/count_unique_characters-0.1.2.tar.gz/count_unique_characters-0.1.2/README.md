# Пакет count_unique_characters

* count_unique_characters - Простий Python-пакет для підрахунку унікальних символів у рядку або файлі.
------------------------------------------------------
# Встановлення

Пакет доступний на PyPI, тож для встановлення достатньо виконати:
```bash
pip install count-unique-characters
```

-------------------------------------------------------
# Використання 

Виклик через Python.

Python-консоль:


```python
from count_unique_characters.core import count_unique_characters

```
Приклад використання:
```python
text = "hello world"
unique_count = count_unique_characters(text)
print(f"Кількість унікальних символів: {unique_count}")
```
Очікуваний результат:

Кількість унікальних символів: 6

--------------------------------------------------------
# Виклик через GitBash:

Встановлення пакета:

```python
(pip install -e .) 
```

Далі

Передача рядка напряму:
```python
count-unique-characters --string "hello world"
```
Передача текстового файлу:
```python
count-unique-characters --file path/to/text.txt
```
**(Заміни path/to/text.txt на реальний шлях до файлу)

--------------------------------------------------------

# Структура проєкту
```python
count_unique_characters/

├── LICENSE

├── pyproject.toml

├── README.md

├── src/ 
└── count_unique_characters/

   └── __init__.py

   └── count_unique_characters.py


├── tests/
```
-------------------------------------------------------

# Тестування
Щоб запустити тести:
```python
 - pytest tests/
```
# Ліцензія

Цей проєкт ліцензовано під MIT. Дивись LICENSE для деталей.