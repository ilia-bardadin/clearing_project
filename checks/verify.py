"""Из корня: python checks/verify.py [--inputs-only | --smoke]. Только чтение."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.util
import sys

import numpy as np

PROJECT = Path(__file__).resolve().parents[1]
CHECKS = PROJECT / 'checks'
DATA = PROJECT / 'stain_data'
RESULTS = PROJECT / 'results'
# Версия выданных входов и эталона; решение агента их не изменяет.
SPECTRA = {
    'tartrazine': (587, 254, 840, 'fed618da48c344e599eddd2f283bd5c64190cb5ab1daeadca0ff823772180079'),
    'indigo_carmine': (1190, 399.49, 1001.21, 'b4df56447348b18007f12210d6760b9f2bd65255326e22d9899103d608602636'),
    'methylene_blue': (301, 200, 800, '812ba1b7c399352968f56c1fcea68babdf3ee7f7cadd06371bec617a721cc7b4'),
    'fluorescein': (1001, 300, 800, '886255cf5b2f74b11bc074ea7aca756133032e1f44951694a64d9dfdfcb01e39'),
}
REFERENCE_SHA256 = 'b38273601c29d568ed0c75e23405add8fde2cbcde028151f15b0671b466ae65a'
POINTS = {'beta_min', 'beta_max', 'alpha_peak', 'near_500_nm', 'near_700_nm', 'near_800_nm'}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_hash(path, expected):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
            f'input_version: изменён файл {path.relative_to(PROJECT)}')


def read_columns(path, columns):
    table = np.genfromtxt(path, delimiter=',', names=True, dtype=float, ndmin=1)
    require(table.dtype.names == columns, f'input/output_schema: {path.name}: нужны {columns}')
    require(table.size > 0, f'input/output_schema: {path.name}: пустая таблица')
    return tuple(table[name] for name in columns)


def load_inputs():
    spectra = {}
    for dye, (size, low, high, digest) in SPECTRA.items():
        path = DATA / f'{dye}_alpha.csv'
        check_hash(path, digest)
        x, a = read_columns(path, ('wavelength_nm', 'alpha_M_inv'))
        require(x.shape == (size,), f'input_grid: {dye}: неверное число узлов')
        require(np.isfinite(x).all() and (x > 0).all() and (np.diff(x) > 0).all(),
                f'input_grid: {dye}: нужна конечная положительная возрастающая сетка')
        np.testing.assert_allclose(x[[0, -1]], [low, high], rtol=0, atol=1e-10)
        np.testing.assert_allclose(np.diff(x), x[1] - x[0], rtol=1e-10, atol=1e-10)
        require(np.isfinite(a).all(), f'input_values: {dye}: неконечная alpha')
        spectra[dye] = (x, a)

    path = CHECKS / 'beta_reference.csv'
    check_hash(path, REFERENCE_SHA256)
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == ['dye', 'point', 'grid_index', 'wavelength_nm', 'beta_M_inv'],
                'reference_schema: неверные столбцы эталона')
        reference = list(reader)
    require(len(reference) == 24 and {r['dye'] for r in reference} == set(SPECTRA),
            'reference_schema: нужны 24 строки для четырёх красителей')
    for dye, (x, _) in spectra.items():
        points = [r for r in reference if r['dye'] == dye]
        require(len(points) == 6 and {r['point'] for r in points} == POINTS,
                f'reference_schema: {dye}: неполный набор контрольных точек')
        for point in points:
            j = int(point['grid_index'])
            require(0 <= j < len(x) and np.isfinite(float(point['beta_M_inv'])),
                    f'reference_values: {dye}: неверный индекс или beta')
            np.testing.assert_allclose(x[j], float(point['wavelength_nm']), rtol=0, atol=1e-10)
    print('OK: входы и эталон — SHA-256, схема, сетки, значения')
    return spectra, reference


def load_function():
    path = PROJECT / 'src' / 'solution.py'
    require(path.is_file(), 'Нет src/solution.py; агент должен реализовать kk_beta')
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('clearing_solution', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    require(callable(getattr(module, 'kk_beta', None)), 'Нет функции kk_beta в src/solution.py')
    return module.kk_beta


def calculate(function, x, a):
    beta = np.asarray(function(x.copy(), a.copy()))
    require(beta.shape == a.shape and np.isrealobj(beta) and np.isfinite(beta).all(),
            'output_values: неверный размер или неконечные/комплексные beta')
    return beta


def check_properties(function):
    # Детерминированные синтетические входы, в том числе со знаком минус.
    for size in (7, 17, 31):
        x = np.linspace(300, 800, size)
        a = np.sin(np.linspace(-2, 3, size))
        b = np.cos(np.linspace(0, 4, size))
        beta = calculate(function, x, a)
        np.testing.assert_allclose(calculate(function, x, np.zeros_like(a)), 0, rtol=0, atol=1e-12)
        np.testing.assert_allclose(calculate(function, x, 2*a), 2*beta, rtol=1e-9, atol=1e-11)
        np.testing.assert_allclose(calculate(function, x, a+b), beta+calculate(function, x, b),
                                   rtol=1e-9, atol=1e-11)
    print('OK: свойства на синтетических сетках 7, 17, 31 узел')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--inputs-only', action='store_true', help='проверить входы без решения')
    mode.add_argument('--smoke', action='store_true', help='входы и свойства функции без выходных CSV')
    args = parser.parse_args()
    spectra, reference = load_inputs()
    if args.inputs_only:
        print('ВХОДЫ ПРОВЕРЕНЫ (решение не проверялось)')
        return
    function = load_function()
    check_properties(function)
    if args.smoke:
        print('КОРОТКАЯ ПРОВЕРКА ПРОЙДЕНА (итоговые CSV не проверялись)')
        return
    for dye, (x, a) in spectra.items():
        beta = calculate(function, x, a)
        errors = []
        for point in (r for r in reference if r['dye'] == dye):
            j, target = int(point['grid_index']), float(point['beta_M_inv'])
            np.testing.assert_allclose(beta[j], target, rtol=1e-7, atol=1e-9,
                                       err_msg=f"{dye}: {point['point']}")
            errors.append(abs(beta[j] - target))
        np.testing.assert_allclose(calculate(function, x, np.zeros_like(a)), 0, rtol=0, atol=1e-12)
        np.testing.assert_allclose(calculate(function, x, 2*a), 2*beta, rtol=1e-9, atol=1e-11)
        saved_x, saved_beta = read_columns(RESULTS / f'{dye}_beta.csv', ('wavelength_nm', 'beta_M_inv'))
        require(saved_x.shape == x.shape and saved_beta.shape == beta.shape,
                f'output_schema: {dye}: неверное число строк CSV')
        require(np.isfinite(saved_x).all() and np.isfinite(saved_beta).all(),
                f'output_values: {dye}: неконечные значения CSV')
        np.testing.assert_allclose(saved_x, x, rtol=0, atol=1e-10)
        np.testing.assert_allclose(saved_beta, beta, rtol=1e-7, atol=1e-9)
        print(f'OK: {dye}; max_abs_error={max(errors):.12g} M^-1')
    print('ПРОЙДЕНО')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'ОШИБКА: {error}')
        sys.exit(1)
