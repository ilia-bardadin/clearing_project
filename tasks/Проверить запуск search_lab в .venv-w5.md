---
type: Задача
status: принята
---
# Проверить запуск search_lab в .venv-w5

Готово, когда: рядом с ноутбуком лежат `library_demo/` и `research_mcp.py` (копии из `week_5/artefacts/`); `jupyter nbconvert --to notebook --execute src/learning_code/search_lab.ipynb` в `.venv-w5` с выводом во временную папку завершается с кодом 0.
Не входит: правка кода ноутбука, сохранение выполненного ноутбука в проект.

## Итог
В `src/learning_code/` скопированы `library_demo/` (corpus.jsonl, corpus_provenance.json) и `research_mcp.py` из `week_5/artefacts/`. Ноутбук прогнан целиком в `.venv-w5`: `jupyter nbconvert --execute` — код 0, 23 ячейки кода без ошибок, сетевые разделы прошли. Прогон сохранил рядом с ноутбуком fig_bm25_saturation.png, fig_openalex_citations.png, fig_projection.png. Заметка: [[Проверка запуска search_lab]].
Принято пользователем: «задача принята»

## Связи
- тип: [[Задача]]
- подзадачаОт: [[Создать окружение .venv-w5 для search_lab]]
