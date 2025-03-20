from typing import List

def latex_table(data: List[List[str]]) -> str:
    col_count = len(data[0]) if data else 0
    cols_format = '|'.join(['c'] * col_count)

    header = "\\begin{tabular}{" + f"|{cols_format}|" + "}\n\\hline\n"
    footer = "\\end{tabular}"

    body = "\\\\ \\hline\n".join(" & ".join(map(str, row)) for row in data)
    body += " \\\\ \\hline\n"

    return header + body + footer
