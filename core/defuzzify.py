# core/defuzzify.py
from core.model import NeutrosophicZNumber


def nzn_def(x: NeutrosophicZNumber) -> float:
    return (
        2
        + x.aA * x.aC
        - x.bA * x.bC
        - x.gA * x.gC
    ) / 3
