import os


def generate_table(table):
    if not all(len(row) == len(table[0]) for row in table):
        raise ValueError("All rows in table should be the same length")
    result = "\\begin{table}[h!]\n\\centering\n\\begin{tabular}{|" \
             + "|".join(["c"] * len(table[0])) + "|}\n\\hline\n"
    for row in table:
        result += " & ".join(map(str, row)) + " \\\\\n\\hline\n"
    result += "\\end{tabular}\n\\end{table}"
    return result


def generate_img(img_path):
    if not os.path.isfile(img_path) and not ".png" in img_path:
        raise ValueError("Incorrect image path")
    result = "\\begin{figure}[h!]\n\\centering\n\\includegraphics{" \
             + img_path + "}\n\\end{figure}\n"
    return result


def get_document(content):
    return "\n\\documentclass{article}\n\\usepackage{graphics}\n\\begin{document}\n" \
           + content + "\\end{document}\n"