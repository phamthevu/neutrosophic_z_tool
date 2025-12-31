# ui/parser.py
import re
from core.model import NeutrosophicZNumber


_PATTERN = re.compile(
    r"""
    \[\s*
    \(\s*([0-9.,]+)\s*;\s*([0-9.,]+)\s*\)\s*;\s*
    \(\s*([0-9.,]+)\s*;\s*([0-9.,]+)\s*\)\s*;\s*
    \(\s*([0-9.,]+)\s*;\s*([0-9.,]+)\s*\)
    \s*\]
    """,
    re.VERBOSE
)


def parse_nzn(text: str) -> NeutrosophicZNumber:
    """
    Strict NZN format:
    [(aA;aC);(bA;bC);(gA;gC)]
    Decimal: . or ,
    """
    m = _PATTERN.fullmatch(text.strip())
    if not m:
        raise ValueError(
            "Sai định dạng NZN.\n"
            "Đúng: [(0.6;0.8);(0.35;0.15);(0.4;0.2)]"
        )

    nums = [float(x.replace(",", ".")) for x in m.groups()]
    return NeutrosophicZNumber(*nums)
