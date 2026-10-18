# STATUS.md

## Где мы
- Задача «Создать окружение .venv-w5 для search_lab» принята пользователем («задача принята»). Обе подзадачи приняты.
- `.venv-w5` — отдельное окружение для учебного ноутбука `src/learning_code/search_lab.ipynb` (Python 3.14.5, sentence-transformers, umap-learn, jupyterlab, mcp, torch). Ядро «Python (.venv-w5 search_lab)» зарегистрировано внутри окружения.
- Рядом с ноутбуком скопированы `library_demo/` и `research_mcp.py` из `week_5/artefacts/`. Полный прогон ноутбука — код 0.
- Прежние задачи (агенты, UNII, ткани) приняты.

## Дальше
- Нет открытых задач. Ждёт новых поручений пользователя.

## Действует
- paper/ только для чтения; числа брать из PDF.
- data/IIR_OCOMM.xls только для чтения.
- Основное окружение `.venv` — без новых пакетов. Учебный ноутбук search_lab запускать в `.venv-w5`:
  `source .venv-w5/bin/activate && cd src/learning_code && jupyter lab search_lab.ipynb`.
