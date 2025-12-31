# core/calculate.py

from core.model import NeutrosophicZNumber


# ==========================================================
# NZN ADDITION (⊕) – Equation (7)
# ==========================================================
def nzn_add(
    x: NeutrosophicZNumber,
    y: NeutrosophicZNumber
) -> NeutrosophicZNumber:

    return NeutrosophicZNumber(
        x.aA + y.aA - x.aA * y.aA,
        x.aC + y.aC - x.aC * y.aC,

        x.bA * y.bA,
        x.bC * y.bC,

        x.gA * y.gA,
        x.gC * y.gC
    )


# ==========================================================
# NZN MULTIPLICATION (⊗) – Equation (8)
# ==========================================================
def nzn_mul(
    x: NeutrosophicZNumber,
    y: NeutrosophicZNumber
) -> NeutrosophicZNumber:

    return NeutrosophicZNumber(
        x.aA * y.aA,
        x.aC * y.aC,

        x.bA + y.bA - x.bA * y.bA,
        x.bC + y.bC - x.bC * y.bC,

        x.gA + y.gA - x.gA * y.gA,
        x.gC + y.gC - x.gC * y.gC
    )


# ==========================================================
# NZN COE (ε ⊗ NZN) – Equation (9)
# ==========================================================
def nzn_coe(
    eps: float,
    x: NeutrosophicZNumber
) -> NeutrosophicZNumber:

    return NeutrosophicZNumber(
        1.0 - (1.0 - x.aA) ** eps,
        1.0 - (1.0 - x.aC) ** eps,

        x.bA ** eps,
        x.bC ** eps,

        x.gA ** eps,
        x.gC ** eps
    )


# ==========================================================
# NZN POW (NZN ^ ε) – Equation (10)
# ==========================================================
def nzn_pow(
    x: NeutrosophicZNumber,
    eps: float
) -> NeutrosophicZNumber:

    return NeutrosophicZNumber(
        x.aA ** eps,
        x.aC ** eps,

        1.0 - (1.0 - x.bA) ** eps,
        1.0 - (1.0 - x.bC) ** eps,

        1.0 - (1.0 - x.gA) ** eps,
        1.0 - (1.0 - x.gC) ** eps
    )
