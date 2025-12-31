# ui/main_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinter import filedialog
from core.aggregate import nzn_waa, nzn_wga
from core.multisheet import aggregate_multisheet
import pandas as pd
from tkinter import filedialog
from core.multisheet import aggregate_multisheet
from PIL import Image, ImageTk
from core.resource import resource_path



from core.calculate import (
    nzn_add, nzn_mul,
    nzn_coe, nzn_pow
)
from core.defuzzify import nzn_def
from ui.parser import parse_nzn

def coe_wrapper(nz, eps):
    from core.calculate import nzn_coe
    return nzn_coe(eps, nz)



from PIL import Image, ImageTk

_formula_cache = {}

def add_formula_image(parent, img_path, width=650):
    img = Image.open(resource_path(img_path))

    w, h = img.size
    scale = width / w
    img = img.resize((int(w * scale), int(h * scale)))

    photo = ImageTk.PhotoImage(img)
    _formula_cache[img_path] = photo  # giữ reference

    lbl = tk.Label(parent, image=photo)
    lbl.pack(pady=8)


def start_app():
    root = tk.Tk()
    root.title("Neutrosophic Z-number Tool")
    root.geometry("900x600")

    style = ttk.Style(root)
    style.configure("TNotebook.Tab", font=("Segoe UI", 12), padding=[14, 8])
    style.configure("TButton", font=("Segoe UI", 11))

    nb = ttk.Notebook(root)
    nb.pack(expand=True, fill="both")

    # ======================================================
    # Helper: binary operation
    # ======================================================
    def binary_tab(title, func, formula_img=None):
        tab = ttk.Frame(nb)
        nb.add(tab, text=title)

        if formula_img:
            add_formula_image(tab, formula_img)

        f = tk.Frame(tab)
        f.pack(pady=20)

        tk.Label(f, text="NZN A").grid(row=0, column=0, sticky="e")
        ea = tk.Entry(f, width=45)
        ea.grid(row=0, column=1, padx=10)

        tk.Label(f, text="NZN B").grid(row=1, column=0, sticky="e")
        eb = tk.Entry(f, width=45)
        eb.grid(row=1, column=1, padx=10)

        er = tk.Entry(f, width=50)
        er.grid(row=3, column=0, columnspan=2, pady=15)

        def calc():
            try:
                A = parse_nzn(ea.get())
                B = parse_nzn(eb.get())
                er.delete(0, tk.END)
                er.insert(0, str(func(A, B)))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(f, text="Calculate", command=calc)\
            .grid(row=2, column=1, pady=10)

    # ======================================================
    # Helper: unary + epsilon
    # ======================================================
    def eps_tab(title, func, formula_img=None):
        tab = ttk.Frame(nb)
        nb.add(tab, text=title)

        if formula_img:
            add_formula_image(tab, formula_img)

        f = tk.Frame(tab)
        f.pack(pady=20)


        tk.Label(f, text="NZN").grid(row=0, column=0, sticky="e")
        en = tk.Entry(f, width=45)
        en.grid(row=0, column=1, padx=10)

        tk.Label(f, text="ε").grid(row=1, column=0, sticky="e")
        ee = tk.Entry(f, width=10)
        ee.grid(row=1, column=1, sticky="w")

        er = tk.Entry(f, width=50)
        er.grid(row=3, column=0, columnspan=2, pady=15)

        def calc():
            try:
                nz = parse_nzn(en.get())
                eps = float(ee.get())
                er.delete(0, tk.END)
                er.insert(0, str(func(nz, eps)))
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(f, text="Calculate", command=calc)\
            .grid(row=2, column=1, pady=10)

    # ======================================================
    # Tabs
    # ======================================================
    binary_tab("SUM", nzn_add, "assets/sum.png")
    binary_tab("MUL", nzn_mul, "assets/mul.png")
    eps_tab("COE", coe_wrapper, "assets/coe.png")
    eps_tab("POW", nzn_pow, "assets/pow.png")

    # DEF
    tab_def = ttk.Frame(nb)

    nb.add(tab_def, text="DEF")
    add_formula_image(tab_def, "assets/def.png")
    nb.add(tab_def, text="DEF")

    f = tk.Frame(tab_def)
    f.pack(pady=30)

    tk.Label(f, text="NZN").grid(row=0, column=0, sticky="e")
    en = tk.Entry(f, width=45)
    en.grid(row=0, column=1, padx=10)

    el = tk.Label(f, text="—", font=("Segoe UI", 13, "bold"))
    el.grid(row=3, column=0, columnspan=2, pady=10)

    def calc_def():
        try:
            nz = parse_nzn(en.get())
            el.config(text=f"DEF = {nzn_def(nz):.4f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(f, text="Calculate", command=calc_def)\
        .grid(row=1, column=1, pady=10)
    

    # ======================================================
    # AGGREGATION TAB (WITH EXCEL IMPORT)
    # ======================================================
    def create_aggregation_tab(title, agg_func, formula_img=None):
        tab = ttk.Frame(nb)
        nb.add(tab, text=title)

        if formula_img:
            add_formula_image(tab, formula_img)

        items = []   # [(NZN, weight)]

        # ---------------- TABLE ----------------
        tree = ttk.Treeview(
            tab,
            columns=("nzn", "w", "nw"),
            show="headings",
            height=10
        )
        tree.heading("nzn", text="NZN")
        tree.heading("w", text="Weight")
        tree.heading("nw", text="Norm weight")

        tree.column("nzn", width=420)
        tree.column("w", width=90, anchor="center")
        tree.column("nw", width=110, anchor="center")

        tree.pack(padx=10, pady=10, fill="both", expand=True)

        # ---------------- HELPERS ----------------
        def refresh():
            tree.delete(*tree.get_children())
            total = sum(w for _, w in items)
            for nz, w in items:
                nw = w / total if total != 0 else 0
                tree.insert("", "end", values=(str(nz), w, round(nw, 4)))

        # ---------------- CONTROLS ----------------
        ctrl = tk.Frame(tab)
        ctrl.pack(pady=5)

        e_nzn = tk.Entry(ctrl, width=40)
        e_nzn.pack(side="left", padx=5)

        e_w = tk.Entry(ctrl, width=8)
        e_w.pack(side="left", padx=5)

        def add_manual():
            try:
                nz = parse_nzn(e_nzn.get())
                w = float(e_w.get())
                items.append((nz, w))
                refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def delete_selected():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            items.pop(idx)
            refresh()

        def import_excel():
            path = filedialog.askopenfilename(
                filetypes=[("Excel file", "*.xlsx *.xls")]
            )
            if not path:
                return

            try:
                df = pd.read_excel(path, header=None)
                items.clear()

                for _, row in df.iterrows():
                    if pd.isna(row[0]) or pd.isna(row[1]):
                        continue
                    nz = parse_nzn(str(row[0]))
                    w = float(row[1])
                    items.append((nz, w))

                refresh()
            except Exception as e:
                messagebox.showerror("Excel import error", str(e))

        def refresh_weight_view():
            weight_tree.delete(*weight_tree.get_children())
            for s, w in zip(excel_ctx["ans_sheets"], excel_ctx["weights"]):
                weight_tree.insert(
                    "",
                    "end",
                    values=(s, round(w, 4))
                )


        tk.Button(ctrl, text="Add", command=add_manual).pack(side="left", padx=5)
        tk.Button(ctrl, text="Delete", command=delete_selected).pack(side="left", padx=5)
        tk.Button(ctrl, text="Import Excel", command=import_excel).pack(side="left", padx=5)

        # ---------------- RESULT ----------------
        res_entry = tk.Entry(tab, width=55)
        res_entry.pack(pady=10)

        def aggregate():
            if not items:
                return
            nzs = [nz for nz, _ in items]
            ws = [w for _, w in items]
            s = sum(ws)
            ws = [w / s for w in ws]

            res = agg_func(nzs, ws)
            res_entry.delete(0, tk.END)
            res_entry.insert(0, str(res))

        tk.Button(tab, text="Aggregate", command=aggregate).pack(pady=5)

    create_aggregation_tab("NZN-WAA", nzn_waa, "assets/waa.png")
    create_aggregation_tab("NZN-WGA", nzn_wga, "assets/wga.png")

    # ======================================================
    # MULTI-SHEET TAB (FULL – PREVIEW | WEIGHT | RESULT | EXPORT)
    # ======================================================
    tab_ms = ttk.Frame(nb)
    nb.add(tab_ms, text="MULTI-SHEET")

    excel_ctx = {
        "xls": None,
        "path": None,
        "ans_sheets": [],
        "weights": [],
        "result": None,
        "row_names": [],
        "col_names": []
    }

    # ------------------------------------------------------
    # READ & NORMALIZE WEIGHTS
    # ------------------------------------------------------
    def read_weights():
        k = len(excel_ctx["ans_sheets"])

        if excel_ctx["xls"] and "Weight" in excel_ctx["xls"].sheet_names:
            wdf = pd.read_excel(
                excel_ctx["xls"],
                sheet_name="Weight",
                header=None
            )
            ws = wdf.iloc[:k, 0].astype(float).tolist()
        else:
            ws = [1.0] * k

        s = sum(ws)
        excel_ctx["weights"] = [w / s for w in ws]

    # ------------------------------------------------------
    # REFRESH WEIGHT VIEW
    # ------------------------------------------------------
    def refresh_weight_view():
        weight_tree.delete(*weight_tree.get_children())
        for s, w in zip(excel_ctx["ans_sheets"], excel_ctx["weights"]):
            weight_tree.insert("", "end", values=(s, round(w, 4)))

    # ------------------------------------------------------
    # LOAD PREVIEW SHEET
    # ------------------------------------------------------
    def load_preview_sheet(sheet_name):
        df = pd.read_excel(
            excel_ctx["xls"],
            sheet_name=sheet_name,
            header=None
        )

        preview_tree.delete(*preview_tree.get_children())

        cols = df.shape[1]
        preview_tree["columns"] = list(range(cols))

        # header row
        for c in range(cols):
            preview_tree.heading(c, text=str(df.iloc[0, c]))
            preview_tree.column(c, width=160)

        # body
        for i in range(1, df.shape[0]):
            preview_tree.insert("", "end", values=df.iloc[i].tolist())

    # ------------------------------------------------------
    # IMPORT EXCEL
    # ------------------------------------------------------
    def import_excel_ms():
        path = filedialog.askopenfilename(
            filetypes=[("Excel", "*.xlsx *.xls")]
        )
        if not path:
            return

        excel_ctx["path"] = path
        excel_ctx["xls"] = pd.ExcelFile(path)

        excel_ctx["ans_sheets"] = [
            s for s in excel_ctx["xls"].sheet_names
            if s.lower().startswith("ans")
        ]

        if not excel_ctx["ans_sheets"]:
            messagebox.showerror("Error", "Không tìm thấy sheet Ans*")
            return

        read_weights()
        refresh_weight_view()

        sheet_cb["values"] = excel_ctx["ans_sheets"]
        sheet_var.set(excel_ctx["ans_sheets"][0])
        load_preview_sheet(excel_ctx["ans_sheets"][0])

    # ------------------------------------------------------
    # DELETE SELECTED SHEET
    # ------------------------------------------------------
    def delete_sheet():
        s = sheet_var.get()
        if not s:
            return

        excel_ctx["ans_sheets"].remove(s)

        if not excel_ctx["ans_sheets"]:
            preview_tree.delete(*preview_tree.get_children())
            weight_tree.delete(*weight_tree.get_children())
            sheet_cb["values"] = []
            return

        read_weights()
        refresh_weight_view()

        sheet_cb["values"] = excel_ctx["ans_sheets"]
        sheet_var.set(excel_ctx["ans_sheets"][0])
        load_preview_sheet(excel_ctx["ans_sheets"][0])

    # ------------------------------------------------------
    # AGGREGATE MULTI-SHEET
    # ------------------------------------------------------
    def aggregate_ms():
        matrices = []
        for s in excel_ctx["ans_sheets"]:
            df = pd.read_excel(
                excel_ctx["xls"],
                sheet_name=s,
                header=None
            )
            matrices.append(df)

        base = matrices[0]
        excel_ctx["col_names"] = base.iloc[0, 1:].tolist()
        excel_ctx["row_names"] = base.iloc[1:, 0].tolist()

        rows, cols = base.shape
        result = [[None] * (cols - 1) for _ in range(rows - 1)]

        agg_func = nzn_waa if method_var.get() == "WAA" else nzn_wga

        for i in range(1, rows):
            for j in range(1, cols):
                items = [
                    parse_nzn(str(mat.iloc[i, j]))
                    for mat in matrices
                ]
                result[i - 1][j - 1] = str(
                    agg_func(items, excel_ctx["weights"])
                )

        excel_ctx["result"] = result

        # -------- RESULT VIEW --------
        result_tree.delete(*result_tree.get_children())
        result_tree["columns"] = ["row"] + list(range(len(excel_ctx["col_names"])))

        result_tree.heading("row", text="")
        result_tree.column("row", width=120)

        for i, c in enumerate(excel_ctx["col_names"]):
            result_tree.heading(i, text=c)
            result_tree.column(i, width=180)

        for r, rn in enumerate(excel_ctx["row_names"]):
            result_tree.insert(
                "",
                "end",
                values=[rn] + excel_ctx["result"][r]
            )

    # ------------------------------------------------------
    # EXPORT RESULT + WEIGHT
    # ------------------------------------------------------
    def export_result():
        if excel_ctx["result"] is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not path:
            return

        # result sheet
        df_res = pd.DataFrame(
            excel_ctx["result"],
            index=excel_ctx["row_names"],
            columns=excel_ctx["col_names"]
        )

        # weight sheet
        df_w = pd.DataFrame({
            "Sheet": excel_ctx["ans_sheets"],
            "Weight": excel_ctx["weights"]
        })

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df_res.to_excel(writer, sheet_name="Result")
            df_w.to_excel(writer, sheet_name="Weight", index=False)

        messagebox.showinfo("OK", "Export thành công")

    # ------------------------------------------------------
    # UI CONTROLS
    # ------------------------------------------------------
    top = tk.Frame(tab_ms)
    top.pack(fill="x", pady=5)

    tk.Button(top, text="Import Excel", command=import_excel_ms)\
        .pack(side="left", padx=5)

    sheet_var = tk.StringVar()
    sheet_cb = ttk.Combobox(
        top, textvariable=sheet_var,
        state="readonly", width=15
    )
    sheet_cb.pack(side="left", padx=5)
    sheet_cb.bind("<<ComboboxSelected>>",
                lambda e: load_preview_sheet(sheet_var.get()))

    tk.Button(top, text="Delete Sheet", command=delete_sheet)\
        .pack(side="left", padx=5)

    method_var = tk.StringVar(value="WAA")
    ttk.Combobox(
        top, textvariable=method_var,
        values=["WAA", "WGA"],
        state="readonly", width=8
    ).pack(side="left", padx=5)

    tk.Button(top, text="Aggregate", command=aggregate_ms)\
        .pack(side="left", padx=10)

    tk.Button(top, text="Export", command=export_result)\
        .pack(side="left", padx=5)

    # ------------------------------------------------------
    # PREVIEW
    # ------------------------------------------------------
    tk.Label(tab_ms, text="Preview", font=("Segoe UI", 11, "bold"))\
        .pack(anchor="w", padx=10)

    preview_tree = ttk.Treeview(tab_ms, show="headings", height=8)
    preview_tree.pack(fill="both", expand=True, padx=10, pady=5)

    # ------------------------------------------------------
    # WEIGHT VIEW
    # ------------------------------------------------------
    tk.Label(tab_ms, text="Weights", font=("Segoe UI", 11, "bold"))\
        .pack(anchor="w", padx=10)

    weight_tree = ttk.Treeview(
        tab_ms,
        columns=("sheet", "weight"),
        show="headings",
        height=5
    )
    weight_tree.heading("sheet", text="Sheet")
    weight_tree.heading("weight", text="Weight")
    weight_tree.column("sheet", width=160)
    weight_tree.column("weight", width=120, anchor="center")
    weight_tree.pack(fill="x", padx=10, pady=3)

    # ------------------------------------------------------
    # RESULT
    # ------------------------------------------------------
    tk.Label(tab_ms, text="Result", font=("Segoe UI", 11, "bold"))\
        .pack(anchor="w", padx=10)

    result_tree = ttk.Treeview(tab_ms, show="headings", height=8)
    result_tree.pack(fill="both", expand=True, padx=10, pady=5)



    root.mainloop()
