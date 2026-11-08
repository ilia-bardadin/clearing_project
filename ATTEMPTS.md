# ATTEMPTS.md — вычислительное направление B, неделя 7

| № | Дата | Подцель | Исполнитель | Действие | Ответ верификатора | Решение |
|---|---|---|---|---|---|---|
| 1 | 2026-11-08 | G1 (output) | AI4Science | `pytest -k "output and not catches"` | 1 passed — свойство формы/действительности/конечности выполняется | Принято |
| 2 | 2026-11-08 | G1 (output) | AI4Science | `pytest -k "output and catches"` | 1 passed — mutant_shape пойман на (200, 201), [0, 0] | Принято |
| 3 | 2026-11-08 | G2 (zero/hom/add) | AI4Science | `pytest -k "zero or homogeneity or additivity and not catches"` | 5 passed — нулевой вход, однородность, аддитивность выполняются | Принято |
| 4 | 2026-11-08 | G2 (zero) | AI4Science | `pytest -k "zero and catches"` | 1 passed — mutant_offset пойман на (200, 201), [0, 0] | Принято |
| 5 | 2026-11-08 | G2 (homogeneity) | AI4Science | `pytest -k "homogeneity and catches"` | 1 passed — mutant_nonlinear пойман на (200, 201), [0, 1], -1 | Принято |
| 6 | 2026-11-08 | G2 (additivity) | AI4Science | `pytest -k "additivity and catches"` | 1 passed — mutant_nonadditive пойман на (200, 201), [0, 1], [1, 0] | Принято |
| 7 | 2026-11-08 | G3 (scale) | AI4Science | `pytest -k "wavelength_scale and not catches"` | 1 passed — инвариантность при масштабе сетки выполняется | Принято |
| 8 | 2026-11-08 | G3 (scale) | AI4Science | `pytest -k "wavelength_scale and catches"` | 1 passed — mutant_wrong_step пойман на (200, 201), [0, 1], 0.001 | Принято |
| 9 | 2026-11-08 | G4 (diagonal) | AI4Science | `pytest -k "diagonal and not catches"` | 1 passed — диагональный вклад исключён | Принято |
| 10 | 2026-11-08 | G4 (diagonal) | AI4Science | `pytest -k "diagonal and catches"` | 1 passed — mutant_diagonal пойман на (200, 201), 0, 1.0 | Принято |
| 11 | 2026-11-08 | G1–G4 | AI4Science | `pytest checks_week7 -q` полная сборка | 14 passed — все 7 свойств + 7 мутантов | Принято |
| 12 | 2026-11-08 | G5 (two_nodes) | AI4Science (подагент) | Вывел аналитическую формулу для N=2, сверил с `check_two_nodes`, запустил тест | 2 passed — формула совпадает, проверка обнаруживает пропуск `2/pi` | Принято |
| 13 | 2026-11-08 | G6 (catches_mutation) | AI4Science (подагент) | Запустил `pytest -k catches_mutation`, проанализировал 7 контрпримеров | 7 passed — все мутанты обнаружены; G5 — единственный абсолютный тест для `2/pi` | Принято |
| 14 | 2026-11-08 | G1–G7 | AI4Science | Итоговая сборка: исправления отчётов, повторная проверка | `pytest checks_week7 -q` → 14 passed; `checks/verify.py` → ПРОЙДЕНО | Принято |

**Правило трёх попыток:** не применяется. Все подцели G1–G7 закрыты с первой попытки.