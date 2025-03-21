import subprocess


def shielding_latex(text):
    replacements = {
        "&": "\\&",
        "%": "\\%",
        "$": "\\$",
        "#": "\\#",
        "_": "\\_",
        "{": "\\{",
        "}": "\\}",
        "~": "\\textasciitilde{}",
        "^": "\\textasciicircum{}",
        "\\": "\\textbackslash{}",
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def generate_table(data):
    col_format = "{c}" if not data or not data[0] else "{" + "c" * len(data[0]) + "}"

    latex = f"\\begin{{tabular}}{col_format}\n"

    for i, row in enumerate(data):
        escaped_row = [shielding_latex(str(cell)) for cell in row]

        latex += " & ".join(escaped_row)

        latex += " \\\\\n" if i < len(data) - 1 else "\n"

    latex += "\\end{tabular}"

    full_document = f"""\\documentclass{{article}}
\\usepackage{{amsmath}}
\\begin{{document}}

{latex}

\\end{{document}}
"""

    return full_document


def generate_image(image_path, width=None, caption=None):
    latex = "\\begin{figure}[h]\n\\centering\n"

    latex += (
        f"\\includegraphics[width={width}]{{{image_path}}}\n"
        if width
        else f"\\includegraphics{{{image_path}}}\n"
    )

    if caption:
        latex += f"\\caption{{{shielding_latex(caption)}}}\n"

    latex += "\\end{figure}"

    full_document = f"""\\documentclass{{article}}
\\usepackage{{graphicx}}
\\begin{{document}}

{latex}

\\end{{document}}
"""

    return full_document


def gererate_latex_and_pdf(latex_document, path_latex):
    with open(path_latex, "w") as f:
        f.write(latex_document)

    subprocess.run(["pdflatex", path_latex], check=True)
