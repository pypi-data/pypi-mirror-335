"""
Damped Newton step
"""


#[

import numpy as _np
import scipy as _sp
import warnings as _wa
from numbers import Real

from . import iterative as _iterative
from ._searches import damped_search

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from . import iterative as _iterative

#]


_INITIAL_KAPPA = 1e-10
_UPSCALING = 10
_KAPPA_CAP = 1e8
_MIN_IMPROVEMENT_RATE = 0


def eval_step(
    guess: _iterative.GuessType,
    func: _iterative.ArrayType,
    jacob: _iterative.SparseArrayType,
    norm: float,
    eval_func: _iterative.FuncEvalType,
    eval_norm: _iterative.NormEvalType,
    *,
    min_improvement_rate: float = _MIN_IMPROVEMENT_RATE,
) -> tuple[_iterative.GuessType, _iterative.ArrayType, Real, ]:
    """
    """

    # solve = _sp.sparse.linalg.spsolve
    # eye = _sp.sparse.eye
    # diag = _sp.sparse.diags

    solve = _sp.linalg.solve
    def lstsq(*args):
        return _sp.linalg.lstsq(*args)[0]

    eye = _np.eye
    diag = _np.diag

    newton = jacob.T @ jacob
    gradient = eye(newton.shape[0], )
    B = -jacob.T @ func

    def _calculate_direction(kappa, ):
        A = newton + kappa * gradient
        try:
            _wa.simplefilter("error", _sp.linalg.LinAlgWarning, )
            direction = solve(A, B, )
            _wa.simplefilter("default", _sp.linalg.LinAlgWarning, )
        except:
            direction = lstsq(A, B, )
        return direction

    def _calculate_candidate(kappa, ):
        new_direction = _calculate_direction(kappa, )
        new_guess = guess + new_direction
        new_func = eval_func(new_guess, )
        new_norm = eval_norm(new_func, )
        return new_guess, new_func, kappa, new_norm,

    def _update_kappa(kappa, ):
        return (
            kappa * _UPSCALING if kappa
            else _INITIAL_KAPPA
        )

    kappa = 0
    while kappa < _KAPPA_CAP:
        *candidate, new_norm = _calculate_candidate(kappa, )
        if new_norm < norm:
            return candidate
        kappa = _update_kappa(kappa, )

    # Fall back to pure gradient step
    direction = B
    new_guess, new_func, new_step_size, = damped_search(
        direction=direction,
        prev_guess=guess,
        min_norm=norm,
        eval_func=eval_func,
        eval_norm=eval_norm,
    )
    kappa = None
    return new_guess, new_func, kappa,


