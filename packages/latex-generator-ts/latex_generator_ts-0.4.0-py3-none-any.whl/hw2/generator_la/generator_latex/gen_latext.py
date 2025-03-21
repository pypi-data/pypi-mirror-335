from functools import reduce
from typing import List


def generate_latex_table(data: List):
    if not data:
        return ""

    columns = len(data[0])

    latex_table = f"\\begin{{tabular}}{{|{'|'.join(['c'] * columns)}|}}\n\\hline\n"

    rows = reduce(
        lambda acc, row: acc + f"{' & '.join(map(str, row))} \\\\\n\\hline\n",
        data,
        latex_table
    )

    latex_table = rows + "\\end{tabular}"

    return latex_table


def create_doc_latex(text: str):
    return '\\begin{document}' + text + '\\end{document}'


def generate_latex_image(image_path: str):
    return f"\\includegraphics{{{image_path}}}"
