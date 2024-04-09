# Заметки

## Токены

С ценной за 1 ед. токена можно ознакомится по [ссылке](https://openai.com/pricing).

### Расчет токенов

Токены считаются по алгоритму [Byte pair encoding](https://en.wikipedia.org/wiki/Byte_pair_encoding). То есть контекст,
который будет иметь одинаковое количество символов и слов, но различное содержание рассчитается по-разному.
Модуль `token_counter.py` позволяет правильно рассчитать количество токенов для запроса к разным OpenAI моделям.

### Context window

У каждой модель разное ограничение по размеру максимального контекстного запроса. К примеру, у модели
**gpt-4-0125-preview** `CONTEXT WINDOW = 128,000 tokens`. Более подробно можно ознакомится
в [документации](https://platform.openai.com/docs/models/overview). 

### Rate limits
[Документация](https://platform.openai.com/docs/guides/rate-limits)
