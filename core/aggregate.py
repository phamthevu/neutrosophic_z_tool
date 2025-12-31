# core/aggregate.py

from core.model import NeutrosophicZNumber
from core.calculate import (
    nzn_add,
    nzn_mul,
    nzn_coe,
    nzn_pow
)


# ==========================================================
# NZNWAA – Weighted Arithmetic Aggregation
# Equation (12)
# ==========================================================
def nzn_waa(
    items: list[NeutrosophicZNumber],
    weights: list[float]
) -> NeutrosophicZNumber:

    if len(items) == 0:
        raise ValueError("items rỗng")

    if len(items) != len(weights):
        raise ValueError("items và weights không cùng độ dài")

    res = nzn_coe(weights[0], items[0])

    for i in range(1, len(items)):
        term = nzn_coe(weights[i], items[i])
        res = nzn_add(res, term)

    return res


# ==========================================================
# NZNWGA – Weighted Geometric Aggregation
# Equation (13)
# ==========================================================
def nzn_wga(
    items: list[NeutrosophicZNumber],
    weights: list[float]
) -> NeutrosophicZNumber:

    if len(items) == 0:
        raise ValueError("items rỗng")

    if len(items) != len(weights):
        raise ValueError("items và weights không cùng độ dài")

    res = nzn_pow(items[0], weights[0])

    for i in range(1, len(items)):
        term = nzn_pow(items[i], weights[i])
        res = nzn_mul(res, term)

    return res
