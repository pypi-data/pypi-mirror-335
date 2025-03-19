def generate_doc(blocks, doc_class="article", packages=None):
    latex_doc = "\documentclass{" + doc_class + "}\n"

    if packages:
        for package in packages:
            latex_doc += "\\usepackage{" + package + "}\n"

    latex_doc += "\\begin{document}\n\n"
    for block in blocks:
        latex_doc += block + "\n"
    latex_doc += "\\end{document}\n"
    return latex_doc


def generate_table(table):
    if len(table) == 0:
        return ""

    n = len(table[0])

    latex_table = "\\begin{tabular}"
    latex_table += "{ |" + "|".join(["c" for _ in range(n)]) + "| }\n"
    latex_table += "\\hline\n"
    for row in table:
        latex_table += " & ".join(map(str, row)) + " \\\\\n"
        latex_table += "\\hline\n"

    latex_table += "\\end{tabular}\n"
    return latex_table


def generate_image(path, width="0.8\linewidth"):
    latex_image = "\\begin{figure}[h]\n"
    latex_image += "\\centering\n"
    latex_image += "\\includegraphics[width=" + width + "]{" + path + "}\n"
    latex_image += "\\end{figure}\n"
    return latex_image
