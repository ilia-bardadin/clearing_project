# INDEX.md — где что лежит

Читать первым. Открывать только файлы, нужные для задачи.

## Правила и состояние
- `AGENTS.md` — правила работы агента в проекте.
- `STATUS.md` — где работа сейчас; читать в начале сессии.
- `diary.md` — журнал проекта; только дописывается.
- `AGENTS_week_2.md` — старая версия AGENTS.md (обзор литературы, неделя 2); не действует.
- `AGENTS_week_1.md` — черновик AGENT.md о поиске новых просветляющих агентов; не действует.
- `promts` — папка с промтами.

## Статьи — только чтение
- `paper/1_Ou_achieving-optical-transparency_2024.pdf` — Ou et al., Science 2024: КК, Eq. 1 и 6, Table 1 (β тартразина).
- `paper/2_zhu_main-principal-toc_2021.pdf` — Yu et al., iScience 2021: обзор механизмов просветления; сжатие — в `memory/`.
- `paper/2_zhu_main-principal-toc_2021.txt` — текст того же обзора; цитаты и страницы сверять по PDF.
- `paper/OCA_Tuchin_2019.pdf` — Tuchin, 2019: просветляющие агенты.
- `paper/library/` — 4 статьи для обзора литературы:
  - `paper/library/1_tuchin_glucose_2006.pdf` — склера кролика in vivo, глюкоза 40 %;
  - `paper/library/2_tuchin_muscle_2016.pdf` — мышечная ткань;
  - `paper/library/3_wang_hyperocmotic_2001.pdf` — гиперосмотические агенты, 2001;
  - `paper/library/4_gallwas_oct-servical_2015.pdf` — ОКТ шейки матки, 2015.
- `paper/parts/` — обзор Yu et al., нарезанный `cascade.sh` на 8 частей с метками [с. N].

## Сжатие статьи (память)
- `memory/L2.md` — тезисы обзора Yu et al. со сверкой по PDF; читать вместо PDF, числа для расчётов брать из PDF.
- `memory/L1.md` — реферат обзора по частям, со страницами.
- `memory/L3.md` — главный результат обзора одной строкой.
- `memory/L1/` — сжатие каждой части (part_01–08), из него собран L1.

## Данные — только чтение
- `data/other/tartrazine_kk_results.csv` — спектр тартразина, `;`: lambda_nm (300–900 нм), alpha_input_M-1 = dn″/dc (М⁻¹), не экстинкция.
- `data/huskinDB.csv` — база проницаемости кожи (549 соединений): SMILES, logkp (см/с), условия опыта, DOI.

## Код
- `src/kramers_kronig.py` — расчёт β(λ) по КК: load_spectrum(), kramers_kronig_beta(), графики; CLI `--input <csv> --outdir <dir>`. Результат не принят, см. `STATUS.md`.
- `src/check_week3.py` — самопроверка недели 3: сжатие, AGENTS.md, INDEX.md, git.
- `checks/check_review.py` — проверка обзора: `python3 checks/check_review.py review/`.
- `cascade.sh` — каскадное сжатие статьи в `memory/` (L1 → L2 → L3).
- `src/learning_code/` — учебный ноутбук «агент в коде» (`src/learning_code/agent_loop.ipynb`) и журнал прогона; к проекту не относится.

## Результаты
- `memory/1.3_03-10-2026_kk-result.csv` — β(λ) первого прогона КК (неверный: ошибка ~6 порядков).
- `memory/1.1_03-10-2026_input-spectrum.png`, `memory/1.2_03-10-2026_kk-result.png` — графики того прогона.
- `review/table.csv` — таблица работ: ткань, агент, концентрация, условия, коэффициент диффузии, DOI.
- `review/draft.md` — черновик обзора со ссылками [doi].
