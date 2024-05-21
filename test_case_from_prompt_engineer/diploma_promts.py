diploma_theme = """
```json
{
   "Задача": "Дипломная работа",
   "Тема": "{diploma_theme}"
}
```
"""

diploma_other_requirements = """
Эти требования должны учитываться при оформлении работы:

```json
{{
    "Требования к работе": "{other_requirements}"
}}
```
"""

diploma_information_source = """
Эти источники должны быть учтены и использованы при составлении работы:

```json
{{
    "Используемые источники": "{information_source}"
}}
```
"""

diploma_any_information = """
Вот перечень пожеланий студента к работе, имей их в виду и опирайся на них при составлении работы:

```json
{{
    "Дополнение к работе": "{any_information}"
}}
```
"""

# Промт плана генерации
diploma_plan_prompt = """
Перед написанием: {TYPE}, тебе нужно составить предварительный план, по которому ты будешь работать. Этот план должен быть в дальнейшем использоваться при составлении {TYPE}. Он должен быть составлен с учетом предыдущей информации от ученика.  Этот план должен соответствовать: {THEME}, и должен выполняться по следующему формату:

```json
{{
   “Тема работы": "{THEME}",
   “Total capacity": [“min”: {WORK_SIZE_MIN}, “max”: {WORK_SIZE_MAX}],
   “Element-номер элемента”: {{“Name”: “Введение”, “Character capacity”: количество символов}},
   “Element-номер элемента”: {{“Chapter number”: номер главы, “Name”: ”Имя главы”, “Character capacity”: количество символов}},
   “Element-номер элемента”: {{“Chapter number”: номер главы, “Paragraph number”: номер параграфа, “Name”: ”Имя параграфа”, “Character capacity”: количество символов}},
   “Element-номер элемента”: {{“Chapter number”: номер главы, “Paragraph number”: номер параграфа, “Name”: ”Имя параграфа”, “Character capacity”: количество символов}},
   (любое количество новых элементов)...,
   “Element-номер элемента”: {{“Name”: “Заключение”, “Character capacity”: количество символов}}
}}
```
"""