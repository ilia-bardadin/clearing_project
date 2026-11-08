"""Оценка роста времени по сохранённым замерам без повторного расчёта спектров.

Из корня: python src/estimate_runtime.py --output results/runtime_estimate.json
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def estimate(path: Path) -> dict:
    with path.open(encoding='utf-8', newline='') as stream:
        rows = [dict(dye=row['dye'], nodes=int(row['nodes']), seconds=float(row['seconds']))
                for row in csv.DictReader(stream)]
    if len(rows) < 2 or any(row['nodes'] < 2 or not math.isfinite(row['seconds'])
                            or row['seconds'] <= 0 for row in rows):
        raise ValueError('Нужны минимум два положительных конечных замера при N >= 2')
    # Выбор пары зависит только от размера, не от получившегося времени.
    low = min(rows, key=lambda row: row['nodes'])
    high = max(rows, key=lambda row: row['nodes'])
    if low['nodes'] == high['nodes']:
        raise ValueError('Для оценки κ нужны разные размеры')
    kappa = math.log(high['seconds'] / low['seconds']) / math.log(high['nodes'] / low['nodes'])

    def predict(size: int) -> float:
        return high['seconds'] * (size / high['nodes']) ** kappa

    predictions = [dict(dye=row['dye'], nodes=row['nodes'],
                        predicted_seconds=predict(row['nodes']), observed_seconds=row['seconds'])
                   for row in rows]
    total = sum(row['predicted_seconds'] for row in predictions)
    return {
        'source': str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path),
        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'pair_selection': 'smallest and largest node counts',
        'selected_measurements': [low, high],
        'formula': 'kappa = log(T2/T1) / log(N2/N1); T(N) = T2 * (N/N2)**kappa',
        'kappa': kappa,
        'predictions': predictions,
        'predicted_four_spectra_kernel_seconds': total,
        'observed_four_spectra_kernel_seconds': sum(row['seconds'] for row in rows),
        'predicted_full_verifier_kernel_seconds': 3 * total + 5 * sum(predict(n) for n in (7, 17, 31)),
        'verifier_call_counts': {'per_real_spectrum': 3, 'per_synthetic_grid': 5},
        'limitations': [
            'One measurement per size, on different dyes; no uncertainty interval.',
            'Predictions cover kk_beta calls only, excluding startup, file IO and verification overhead.',
            'An approximate model for the current workload, not a convergence order or a large-grid guarantee.',
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PROJECT / 'results' / 'benchmark.csv')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = estimate(args.input.resolve())
    output = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(output, encoding='utf-8')
    print(output, end='')


if __name__ == '__main__':
    main()
