def generate_table(data):
    if not data or not all(isinstance(row, list) for row in data):
        raise ValueError("Input must be a non-empty 2D list")
    
    num_columns = len(data[0])
    if not all(len(row) == num_columns for row in data):
        raise ValueError("All rows must have the same number of columns")
    
    latex_code = [
        "\\begin{tabular}{|" + "c|" * num_columns + "}",
        "\\hline"
    ]
    
    for row in data:
        latex_row = " & ".join(map(str, row)) + " \\\\"
        latex_code.append(latex_row)
        latex_code.append("\\hline")
    
    latex_code.append("\\end{tabular}\n")
    
    return "\n".join(latex_code)

def generate_image(image_path, caption="Example Image", width=r"\textwidth"):
    return f"""
\\begin{{figure}}[htbp]
    \\centering
    \\includegraphics[width={width}]{{{image_path}}}
    \\caption{{{caption}}}
\\end{{figure}}
"""

def generate_document(filename, data):
    with open(filename, "w") as f:
        f.write("\\documentclass{article}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage{graphicx}")
        f.write("\\begin{document}\n\n")
        f.write(data)
        f.write("\\end{document}\n")
