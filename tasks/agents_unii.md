---
type: Задача
status: выполнена
---
# Собрать review/agents_unii.csv: агент × статья × UNII

Запрос пользователя: «Извлеки просветляющие агенты из статей paper/library/, найди каждый в базе data/IIR_OCOMM.xls и собери review/agents_unii.csv: агент, статья, UNII. Готово, когда: в таблице есть каждая пара агент × статья, UNII взяты только из IIR (если агента нет или подходит несколько записей — так и пометь)»

Готово, когда: в `review/agents_unii.csv` по строке на каждую комбинацию агент × статья из paper/library/; UNII взяты из IIR, отсутствующие отмечены как `NOT_FOUND`

Не входит: создание заметок в notes/, онтологии, обзора

## Итог

Создан `review/agents_unii.csv` — 7 строк, каждая пара агент × статья из 4 PDF-статей:

| Агент | Статья | UNII из IIR |
|---|---|---|
| glucose | Tuchin 2006 | NOT_FOUND |
| glucose | Tuchin 2016 | NOT_FOUND |
| ethylene glycol | Tuchin 2016 | NOT_FOUND |
| glycerol | Wang 2001 | NOT_FOUND |
| propylene glycol | Wang 2001 | 6DC9Q167V3 |
| DMSO | Gallwas 2015 | YOW8V9698H |
| PEG (MW 400) | Gallwas 2015 | B697894SGQ |

**Не найдены в IIR:** glucose, ethylene glycol, glycerol — в базе отсутствуют как отдельные ингредиенты (только производные: methyl glucose, diethylene glycol, phosphatidylglycerol).

**PEG (MW 400)** — в статье указано «PEG (MW 400)», в IIR найден «POLYETHYLENE GLYCOL 400» (UNII B697894SGQ).

## Связи
- тип: [[Задача]]