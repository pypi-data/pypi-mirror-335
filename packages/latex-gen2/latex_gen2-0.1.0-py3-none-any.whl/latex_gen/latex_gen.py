def generate_latex_table(data):

    if not data or not all(isinstance(row, list) for row in data):
        raise ValueError("Input data must be a non-empty list of lists")
    
    num_cols = len(data[0])
    if not all(len(row) == num_cols for row in data):
        raise ValueError("All rows must have the same number of columns")
    
    latex = "\\begin{table}[h]\n"
    latex += "    \\centering\n"
    latex += "    \\renewcommand{\\arraystretch}{1.2}\n"
    
    col_format = "|".join(["c"] * num_cols)
    latex += f"    \\begin{{tabular}}{{|{col_format}|}}\n"
    latex += "        \\hline\n"
    
    header_row = " & ".join(f"\\textbf{{{cell}}}" for cell in data[0])
    latex += f"        {header_row} \\\\ \n"
    latex += "        \\hline\n"
    
    for row in data[1:]:
        row_str = " & ".join(str(cell) for cell in row)
        latex += f"        {row_str} \\\\ \n"
        latex += "        \\hline\n"
    
    latex += "    \\end{tabular}\n"
    latex += "    \\caption{Example Table}\n"
    latex += "    \\label{tab:example}\n"
    latex += "\\end{table}\n"
    
    return latex

def generate_latex_image(image_path, caption="Example Image", label="fig:example", width="0.8\\textwidth"):

    latex = "\\begin{figure}[h]\n"
    latex += "    \\centering\n"
    latex += f"    \\includegraphics[width={width}]{{{image_path}}}\n"
    latex += f"    \\caption{{{caption}}}\n"
    latex += f"    \\label{{{label}}}\n"
    latex += "\\end{figure}\n"
    return latex

import subprocess
import os

def generate_full_document(content):

    document = "\\documentclass{article}\n"
    document += "\\usepackage[utf8]{inputenc}\n"
    document += "\\usepackage{graphicx}\n"
    document += "\\usepackage{array}\n"
    document += "\\begin{document}\n"
    document += content
    document += "\\end{document}\n"
    return document

def compile_pdf(latex_code, output_filename="output.pdf"):

    tex_filename = "temp_document.tex"
    with open(tex_filename, "w", encoding="utf-8") as tex_file:
        tex_file.write(latex_code)
    
    try:
        subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], check=True)
        if os.path.exists("temp_document.pdf"):
            os.rename("temp_document.pdf", output_filename)
    except subprocess.CalledProcessError as e:
        print("Ошибка при компиляции PDF:", e)
    finally:
        for ext in [".aux", ".log", ".tex"]:
            fname = "temp_document" + ext
            if os.path.exists(fname):
                os.remove(fname)
