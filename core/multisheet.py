# core/multisheet.py

import pandas as pd
from core.aggregate import nzn_waa, nzn_wga
from ui.parser import parse_nzn


def aggregate_multisheet(
    excel_path: str,
    method: str = "WAA"
):
    """
    method: 'WAA' or 'WGA'
    return: DataFrame NZN
    """

    xls = pd.ExcelFile(excel_path)

    ans_sheets = [s for s in xls.sheet_names if s.lower().startswith("ans")]
    if not ans_sheets:
        raise ValueError("Không tìm thấy sheet Ans*")

    matrices = []
    for s in ans_sheets:
        df = pd.read_excel(xls, sheet_name=s, header=None)
        matrices.append(df)

    # ---------------- weights ----------------
    if "Weight" in xls.sheet_names:
        w_df = pd.read_excel(xls, sheet_name="Weight", header=None)
        weights = w_df.iloc[:, 0].astype(float).tolist()
    else:
        weights = [1 / len(matrices)] * len(matrices)

    if len(weights) != len(matrices):
        raise ValueError("Số weight không khớp số sheet")

    s = sum(weights)
    weights = [w / s for w in weights]

    # ---------------- aggregation ----------------
    rows, cols = matrices[0].shape
    result = [[None] * cols for _ in range(rows)]

    agg_func = nzn_waa if method == "WAA" else nzn_wga

    for i in range(rows):
        for j in range(cols):
            items = [
                parse_nzn(str(mat.iloc[i, j]))
                for mat in matrices
            ]
            result[i][j] = str(agg_func(items, weights))

    return pd.DataFrame(result)
