"""Расчёт beta по alpha через дискретное соотношение Крамерса—Кронига.

Задача 6-1: для четырёх красителей из stain_data/ вычислить молярный
инкремент действительной части показателя преломления beta по заданной
alpha. Чистая функция kk_beta; CLI считает спектры и пишет результаты
в results/.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / 'stain_data'
RESULTS = PROJECT / 'results'

SPECTRA = ('tartrazine', 'indigo_carmine', 'methylene_blue', 'fluorescein')


def kk_beta(wavelength_nm: np.ndarray, alpha_M_inv: np.ndarray) -> np.ndarray:
    """Дискретное КК-преобразование alpha -> beta на равномерной сетке.

    beta[j] = (2/pi) * h * sum_{k != j} alpha[k] / (w[k] * (1 - (w[k]/w[j])**2)),
    где h = w[1] - w[0]. Диагональный член исключается; у остальных узлов
    полный вес h. Сглаживание и поправки не применяются.
    """
    w = np.asarray(wavelength_nm, dtype=float)
    a = np.asarray(alpha_M_inv, dtype=float)
    if w.shape != a.shape or w.ndim != 1 or w.size < 2:
        raise ValueError('kk_beta: нужны одномерные массивы одинаковой длины (>=2)')
    if not (np.isfinite(w).all() and (w > 0).all() and (np.diff(w) > 0).all()):
        raise ValueError('kk_beta: сетка должна быть конечной положительной возрастающей')
    if not np.isfinite(a).all():
        raise ValueError('kk_beta: alpha должна быть конечной')

    h = w[1] - w[0]
    # Матрица весов W[j, k] = 1 / (w[k] * (1 - (w[k]/w[j])**2)), диагональ = 0.
    ratio = w[None, :] / w[:, None]          # (n, n): w[k]/w[j]
    denom = w[None, :] * (1.0 - ratio**2)    # (n, n)
    with np.errstate(divide='ignore', invalid='ignore'):
        weights = np.where(np.eye(w.size, dtype=bool), 0.0, 1.0 / denom)
    beta = (2.0 / np.pi) * h * (weights @ a)
    return beta


def _read_alpha(path: Path) -> tuple[np.ndarray, np.ndarray]:
    table = np.genfromtxt(path, delimiter=',', names=True, dtype=float)
    return table['wavelength_nm'].astype(float), table['alpha_M_inv'].astype(float)


def _write_beta(dye: str, w: np.ndarray, beta: np.ndarray) -> None:
    out = RESULTS / f'{dye}_beta.csv'
    with out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['wavelength_nm', 'beta_M_inv'])
        for x, b in zip(w, beta):
            writer.writerow([f'{x:.17g}', f'{b:.17g}'])


def run_all() -> None:
    RESULTS.mkdir(exist_ok=True)
    runs = []
    for dye in SPECTRA:
        w, a = _read_alpha(DATA / f'{dye}_alpha.csv')
        t0 = time.perf_counter()
        beta = kk_beta(w, a)
        dt = time.perf_counter() - t0
        _write_beta(dye, w, beta)
        runs.append({'dye': dye, 'nodes': w.size, 'seconds': f'{dt:.6f}'})
        print(f'{dye}: {w.size} узлов, beta в {RESULTS / (dye + "_beta.csv")} ({dt:.4f} s)')
    with (RESULTS / 'runs.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['dye', 'nodes', 'seconds'])
        writer.writeheader()
        writer.writerows(runs)
    print(f'журнал: {RESULTS / "runs.csv"}')


def benchmark() -> None:
    """Замеры времени для раздела 8: полный прогон и прогноз на большие сетки."""
    RESULTS.mkdir(exist_ok=True)
    rows = []
    for dye in SPECTRA:
        w, a = _read_alpha(DATA / f'{dye}_alpha.csv')
        t0 = time.perf_counter()
        kk_beta(w, a)
        dt = time.perf_counter() - t0
        rows.append({'dye': dye, 'nodes': w.size, 'seconds': f'{dt:.6f}'})
        print(f'{dye}: n={w.size}, t={dt:.4f} s')
    with (RESULTS / 'benchmark.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['dye', 'nodes', 'seconds'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'замеры: {RESULTS / "benchmark.csv"}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', action='store_true', help='замеры времени')
    args = parser.parse_args()
    if args.benchmark:
        benchmark()
    else:
        run_all()


if __name__ == '__main__':
    main()