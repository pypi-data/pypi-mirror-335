def generate_table_latex(table_data):
    if not table_data:
        return ""
    num_cols = len(table_data[0])
    if any(len(row) != num_cols for row in table_data):
        raise ValueError("Все строки таблицы должны иметь одинаковую длину")

    num_cols = len(table_data[0])
    col_spec = "|".join(["c"] * num_cols)

    latex = "\\begin{table}[h]\n\\centering\n"
    latex += f"\\begin{{tabular}}{{|{col_spec}|}}\n\\hline\n"

    for row in table_data:
        latex += " & ".join(str(cell) for cell in row) + " \\\\ \\hline\n"

    latex += "\\end{tabular}\n"
    latex += "\\caption{Example table}\n"
    latex += "\\label{tab:example}\n"
    latex += "\\end{table}\n"

    return latex


def generate_image_latex(image_path, caption="Example image"):
    latex = "\\begin{figure}[h]\n\\centering\n"
    latex += f"\\includegraphics[width=0.5\\textwidth]{{{image_path}}}\n"
    latex += f"\\caption{{{caption}}}\n"
    latex += "\\label{fig:example}\n"
    latex += "\\end{figure}\n"
    return latex
