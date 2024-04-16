from docx import Document

from ai_module.document_creator.document import init_styles, write_chapter

plan = {
    "Введение": [],
    "Глава 1. Основные положения ликвидации юридических лиц": [
        "1.1. Основания и способы ликвидации юридических лиц.",
        "1.2. Ликвидация вследствие признания организации (юридического лица) банкротом."
    ],
    "Глава 2. Порядок ликвидации": [
        "2.1. Процедура ликвидации юридического лица.",
        "2.2. Выплаты денежных сумм кредиторам. Завершение ликвидации."
    ],
    "Глава 3. Проблемные вопросы ликвидации юридических лиц": [
        "3.1. Новеллы в ликвидации юридических лиц",
        "3.2. Основные проблемы при ликвидации юридических лиц."
    ],
    "Заключение": [],
    "Список используемой литературы": []
}

lorem_test = (
    "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the "
    "industry's standard dummy text ever since the 1500s, when an"
)

doc = Document()
init_styles(doc)
for first_level in plan.keys():
    if len(plan[first_level]):
        for second_level in plan[first_level]:
            write_chapter(doc, second_level, lorem_test, 1)
        continue
    write_chapter(doc, first_level, lorem_test, 0)

doc.save('document.docx')