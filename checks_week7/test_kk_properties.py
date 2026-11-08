"""Week 7: seven properties of the fixed discrete KK transform."""
from pathlib import Path
import importlib.util

import numpy as np
import pytest
from hypothesis import find, given, settings, strategies as st

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "week7_solution", PROJECT / "src" / "solution.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
kk_beta = module.kk_beta

RTOL = 1e-9
ATOL = 1e-11

def result(function, x, a):
    value = np.asarray(function(x.copy(), a.copy()))
    assert value.shape == a.shape, "Wrong output shape"
    assert np.isrealobj(value), "Complex output"
    assert np.isfinite(value).all(), "Nonfinite output"
    return value

def check_zero(function, x, a):
    actual = result(function, x, np.zeros_like(a))
    np.testing.assert_allclose(actual, 0, rtol=0, atol=1e-12)

def check_homogeneity(function, x, a, scale):
    actual = result(function, x, scale * a)
    expected = scale * result(function, x, a)
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)

def check_additivity(function, x, a, b):
    actual = result(function, x, a + b)
    expected = result(function, x, a) + result(function, x, b)
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)

def check_wavelength_scale(function, x, a, scale):
    actual = result(function, scale * x, a)
    expected = result(function, x, a)
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL)

def check_diagonal(function, x, index, amplitude):
    a = np.zeros_like(x)
    a[index] = amplitude
    actual = result(function, x, a)
    np.testing.assert_allclose(actual[index], 0, rtol=0, atol=1e-12)

def check_two_nodes(function, x, a):
    left, right = x
    expected = (2 / np.pi) * np.array([
        -a[1] * left**2 / (right * (left + right)),
        a[0] * right**2 / (left * (left + right)),
    ])
    np.testing.assert_allclose(
        result(function, x, a), expected, rtol=RTOL, atol=ATOL
    )

def check_output(function, x, a):
    result(function, x, a)

def mutant_offset(x, a):
    return kk_beta(x, a) + 1

def mutant_nonlinear(x, a):
    return kk_beta(x, a * a)

def mutant_nonadditive(x, a):
    return kk_beta(x, a) + np.linalg.norm(a)

def mutant_wrong_step(x, a):
    return kk_beta(x, a) / (x[1] - x[0])

def mutant_diagonal(x, a):
    return kk_beta(x, a) + a

def mutant_prefactor(x, a):
    return (np.pi / 2) * kk_beta(x, a)

def mutant_shape(x, a):
    return kk_beta(x, a)[:-1]

VALUES = st.floats(
    min_value=-10, max_value=10,
    allow_nan=False, allow_infinity=False, allow_subnormal=False,
)

@st.composite
def grids(draw, nodes=None):
    n = nodes if nodes is not None else draw(st.integers(2, 48))
    start = draw(st.floats(200, 1200, allow_nan=False, allow_infinity=False))
    step = draw(st.floats(0.25, 10, allow_nan=False, allow_infinity=False))
    return start + step * np.arange(n, dtype=float)

@st.composite
def samples(draw, vectors=1, nodes=None):
    x = draw(grids(nodes=nodes))
    arrays = [
        np.array(draw(st.lists(VALUES, min_size=len(x), max_size=len(x))))
        for _ in range(vectors)
    ]
    return (x, *arrays)

@st.composite
def impulses(draw):
    x = draw(grids())
    index = draw(st.integers(0, len(x) - 1))
    amplitude = draw(VALUES)
    return x, index, amplitude

SCALED_ALPHA = st.tuples(samples(), st.integers(-4, 4)).map(
    lambda case: (*case[0], case[1])
)
SCALED_GRID = st.tuples(samples(), st.sampled_from([0.001, 1000.0])).map(
    lambda case: (*case[0], case[1])
)

PROPERTIES = [
    pytest.param(check_zero, samples(), mutant_offset, id="zero"),
    pytest.param(
        check_homogeneity, SCALED_ALPHA, mutant_nonlinear, id="homogeneity"
    ),
    pytest.param(
        check_additivity, samples(vectors=2),
        mutant_nonadditive, id="additivity"
    ),
    pytest.param(
        check_wavelength_scale, SCALED_GRID, mutant_wrong_step,
        id="wavelength_scale"
    ),
    pytest.param(check_diagonal, impulses(), mutant_diagonal, id="diagonal"),
    pytest.param(
        check_two_nodes, samples(nodes=2), mutant_prefactor, id="two_nodes"
    ),
    pytest.param(check_output, samples(), mutant_shape, id="output"),
]

PROPERTY_SETTINGS = settings(
    max_examples=100, deadline=None, database=None, derandomize=True
)
MUTATION_SETTINGS = settings(
    max_examples=1000, deadline=None, database=None, derandomize=True
)

@pytest.mark.parametrize("check,strategy,mutant", PROPERTIES)
@PROPERTY_SETTINGS
@given(data=st.data())
def test_property(check, strategy, mutant, data):
    args = data.draw(strategy, label="inputs")
    check(kk_beta, *args)

def rejects(check, function, args):
    try:
        check(function, *args)
    except AssertionError:
        return True
    return False

@pytest.mark.parametrize("check,strategy,mutant", PROPERTIES)
def test_property_catches_mutation(check, strategy, mutant):
    counterexample = find(
        strategy,
        lambda args: rejects(check, mutant, args),
        settings=MUTATION_SETTINGS,
    )
    check(kk_beta, *counterexample)
    with pytest.raises(AssertionError):
        check(mutant, *counterexample)
    print(f"{mutant.__name__}: {counterexample!r}")
