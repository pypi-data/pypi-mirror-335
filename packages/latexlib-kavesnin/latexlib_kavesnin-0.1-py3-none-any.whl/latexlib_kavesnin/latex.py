def generate_latex_table(data):
    if not data:
        return "\\begin{tabular}{}\n\\end{tabular}"
    num_columns = len(data[0])
    align = 'l' * num_columns
    latex = "\\begin{tabular}{" + align + "}\n"
    for row in data:
        latex += " & ".join(map(str, row)) + " \\\\\n"
    latex += "\\end{tabular}"
    return latex

def generate_latex_image(image_path):
    latex = "\\begin{figure}[h!]\n"
    latex += "\\centering\n"
    latex += f"\\includegraphics{{{image_path}}}\n"
    latex += "\\end{figure}\n"
    return latex