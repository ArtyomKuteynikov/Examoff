from openai import OpenAI

# Ответы пользователя
TYPE = "Курсовая работа"
THEME = "Политика Петра 1."
WORK_SIZE = 20
WORK_SIZE_MIN = WORK_SIZE*1800
WORK_SIZE_MAX = WORK_SIZE_MIN+3600
OTHER_REQUIREMENTS = "Гост"
INFORMATION_SOURCE = "Интернет"
ANY_INFORMATION = "Пропустить"


# Общий промт
GENERAL_PROMPT = """
Ты играешь роль универсального помощника по написанию учебных работ. Ты профессиональный публицист, специализирующийся на написании научных работ. Ты должен составлять учебные работы связанные с научной публицистикой на уровне учеников школ и вузов, а также отвечать на вопросы по присылаемым тебе материалам по запросам учеников. Ответы на любые запросы ты даешь в JSON формате в блоке кода. В случае если ты принимаешь вводимые данные, ты отвечаешь данный текст без дополнений:

```json
{
	“Flood”: “твой комментарий, не превышающий 100 символов в длину”,
	“Status”: 1 
}
```

Если при обработке запроса была вызвана ошибка, или твое непонимание, ты отвечаешь данный текст:

```json
{
	“Flood”: “твой комментарий, не превышающий 100 символов в длину”,
	“Status”: 0
}
```

Помимо представленных конструкций json ты не даешь никаких ответов кроме тех, что обозначены как исключения. Отчеты по каждому из пунктов не нужны. Ты отвечаешь иначе только при генерации плана работы и текста самой работы, там ты выводишь сообщение в json формате в соответствии с тем, какой формат тебе задают. 

Все дальнейшие действия будут поделены на этапы. Все что ты должен делать после прохождения этапа - выдавать стандартный ответ и ожидать нового этапа. Ты не должен приступать к генерации информации до тех пор, пока тебя об этом не попросят в одном из этапов.
"""

# Промт плана генерации
PLAN_PROMPT = """
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

Общая сумма значений Character capacity должна быть в пределах значения Total capacity. Элементов должно быть много, у каждой главы должно быть в среднем от 2 до 5 параграфов.
"""

# Промт плана генерации
DIPLOMA_PLAN_PROMPT = """
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

Общая сумма значений Character capacity должна быть в пределах значения Total capacity. Элементов должно быть много, у каждой главы должно быть в среднем от 2 до 5 параграфов.
"""

# Промт работы (Курсовая)
CHAPTER_PROMPT = """
Ты должен составить {TYPE}, опираясь на информацию полученную из других этапов.  Ты должен генерировать работу по ее отдельным элементам, в соответствии с планом. Ты должен соответствовать объему текста, который указан в Character capacity соответствующего элемента. Ты можешь его превысить, но не должен сделать меньше. Все элементы должны быть взаимосвязаны и учитывать друг друга при генерации, избегая тавтологии. Каждый элемент должен быть описан максимально объемно и доходчиво, с большим вниманием к деталям и широким спектром информации. Каждый генерируемый элемент является исключением, что обходит стандартное форомление и должен соответствовать следующему формату:

```json
{{
 	“Element-{ELEMENT_NUM}”: “{ELEMENT_NAME}”,
 	“Минимальная сумма символов в Content”: {CHAR_CAPPACITY},
 	“Content”: “Твой ответ, объем символов в котором будет соответствовать "Минимальная сумма символов в Content"”
}}
```
Если {CHAR_CAPPACITY} превысит 2000, то продолжи генерируемый тобой текст в следуюем соощении, и генерируй его, беря это в учет.
"""

# Промт цикла генерации
GENERATOR_PROMPT = """
Перепроверь контекст и продолжай генерацию, которая является исключением, что обходит стандартный формат и использует:

```json
{{
 	“Element-{ELEMENT_NUM}”: “{ELEMENT_NAME}”,
 	“Минимальная сумма символов в Content”: {CHAR_CAPPACITY},
 	“Content”: “Твой ответ, объем символов в котором будет соответствовать "Минимальная сумма символов в Content"”
}}
```
"""


ASK_WORK_SIZE = """
Ты должен оценить объем работы, указав при этом сколько символов потребуется на написание данной работы. В среднем на одну страницу нужно 2000 символов.
Объем работы: {USER_ANSWER}

```json
{{
   "Минимальный объем символов": [Объем символов],
   "Максимальный объем символов": [Объем символов + X]
}}
```
"""

ACCEPT_WORK_PLAN = """
Ты должен оценить объем работы, указав при этом сколько символов потребуется на написание данной работы. В среднем на одну страницу нужно 3000 символов.
Объем работы: {USER_ANSWER}

```json
{{
   "Минимальный объем символов": [Объем символов],
   "Максимальный объем символов": [Объем символов + X]
}}
```
"""