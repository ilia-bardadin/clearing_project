---
type: Отчет
---
# Поиск по своей библиотеке: optical clearing agents skin diffusion

[источник] OpenAlex, запрос: https://api.openalex.org/works?search=optical+clearing+agents+skin+diffusion&per_page=50&filter=has_abstract%3Atrue&select=id%2Cdoi%2Cdisplay_name%2Cpublication_year%2Ccited_by_count%2Cabstract_inverted_index, дата: 2026-10-18, работ: 20

## which optical clearing agents are used for biological tissues

| место | BM25 | вектор |
|---|---|---|
| 1 | Optical coherence tomography imaging depth enhancement by su (W1991332508) | Recent progress in tissue optical clearing (W1570588423) |
| 2 | Recent progress in tissue optical clearing (W1570588423) | Diffusion of optical clearing agents in skin by two-photon m (W2922942185) |
| 3 | Typical application of skin diffusion optical model to quant (W1994709715) | Optical coherence tomography imaging depth enhancement by su (W1991332508) |

[написано] Подходят обзор W1570588423 (механизмы просветления и способы ускорить проникновение агентов) и W2922942185 (глицерин, пропиленгликоль, глюкоза на коже человека). Вектор ставит обзор первым, а BM25 — статью про ОКТ W1991332508 и модель диффузии W1994709715: в них часто повторяются слова «optical clearing agent», хотя перечня агентов нет.

## diffusion coefficient of optical clearing agent in skin

| место | BM25 | вектор |
|---|---|---|
| 1 | Quantitative analysis of dehydration in porcine skin for ass (W2072014991) | Quantitative Evaluation of Optical Clearing Agent Performanc (W4412833239) |
| 2 | Comparing the Effects of Chemical Optical Clearing Agents an (W7171132189) | Diffusion of optical clearing agents in skin by two-photon m (W2922942185) |
| 3 | Measuring the effects of topically applied skin optical clea (W1988116371) | Diffusion of optical clearing agents in skin studied by two- (W2299840662) |

[написано] Подходит векторная выдача: W4412833239 (диффузия агента в коже по закону Фика) и W2922942185 / W2299840662 (модель свободной диффузии глицерина, пропиленгликоля и глюкозы); последние две — одна работа в двух записях OpenAlex. BM25 поднимает работы с теми же словами, но о другом: обезвоживание (W2072014991), сравнение агентов со сжатием (W7171132189), лазерная терапия (W1988116371).

## requirements for optical clearing agent? (refractive index, osmolarity, biocompatibility, toxicity and other)

| место | BM25 | вектор |
|---|---|---|
| 1 | Measuring the effects of topically applied skin optical clea (W1988116371) | Quantitative Evaluation of Optical Clearing Agent Performanc (W4412833239) |
| 2 | Optical clearing of skin using flashlamp-induced enhancement (W2115419584) | Estimation of dehydration of skin by refractometric method u (W2969489268) |
| 3 | Quantitative Evaluation of Optical Clearing Agent Performanc (W4412833239) | Quantitative analysis of dehydration in porcine skin for ass (W2072014991) |

[написано] Прямого перечня требований к агенту нет ни в одной выдаче; ближе всего W2115419584 у BM25 (согласование показателя преломления) и W2969489268, W2072014991 у вектора (обезвоживание — осмотическое действие агента). BM25 цепляется за слова «refractive index», вектор — за смысл «осмолярность → обезвоживание»; обзор W1570588423, где критерии вероятнее всего, не подняла ни одна модель.

## penetration pathways of clearing agents through stratum corneum: intercellular, transcellular, follicular, enhancers

| место | BM25 | вектор |
|---|---|---|
| 1 | Optical clearing of human skin: comparative study of permeab (W2119477416) | Quantitative Evaluation of Optical Clearing Agent Performanc (W4412833239) |
| 2 | Quantitative Evaluation of Optical Clearing Agent Performanc (W4412833239) | Enhancement of transepidermal skin clearing agent delivery u (W2024433090) |
| 3 | Measuring the effects of topically applied skin optical clea (W1988116371) | Optical Clearing of Skin (W2489210201) |

[написано] Подходят W2119477416 у BM25 (проницаемость интактного и перфорированного рогового слоя) и W2024433090, W2489210201 у вектора (разрушение рогового слоя лазером 980 нм; глава о барьере рогового слоя). Конкретные пути — межклеточный, трансцеллюлярный, фолликулярный — не названы ни в одной аннотации; BM25 держится за слова «stratum corneum», вектор находит работы о доставке агента через эпидермис.

## practical applications of optical clearing: OCT imaging depth, laser therapy, diagnostics

| место | BM25 | вектор |
|---|---|---|
| 1 | Optical coherence tomography imaging depth enhancement by su (W1991332508) | Optical coherence tomography imaging depth enhancement by su (W1991332508) |
| 2 | Enhancement of transepidermal skin clearing agent delivery u (W2024433090) | Recent progress in tissue optical clearing (W1570588423) |
| 3 | Measuring the effects of topically applied skin optical clea (W1988116371) | Measuring the effects of topically applied skin optical clea (W1988116371) |

[написано] Подходят обе выдачи: W1991332508 (глубина изображения в ОКТ) на первом месте у обеих и W1988116371 (лазерная терапия: винные пятна, удаление волос и татуировок) на третьем. Выдачи совпадают на 2 из 3 мест и различаются только вторым: у BM25 доставка агента лазером W2024433090, у вектора обзор W1570588423.

Копия отчёта ячейки 14 ноутбука [[src/learning_code/search_lab.ipynb]] (исходный файл — [[src/learning_code/my_search_report.md]]).

## Связи
- тип: [[Отчет]]
- выполняет: [[Положить отчёт о поиске в reports]]
