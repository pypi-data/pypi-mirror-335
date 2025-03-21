def generate_latex_table(data, alignment='c'):
    if not data:
        return ""

    num_columns = len(data[0])
    for row in data:
        assert len(row) == num_columns
            
    
    column_spec = alignment * num_columns
    latex = [f"\\begin{{{'tabular'}}}{{{column_spec}}}"]
    
    for row in data:
        escaped_row = [escape_latex(cell) for cell in row]
        latex_line = " & ".join(escaped_row) + " \\\\"
        latex.append(latex_line)
    
    latex.append("\\end{tabular}")
    return "\n".join(latex)

def escape_latex(s):
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    s = str(s)
    for find, replace in replacements.items():
        s = s.replace(find, replace)
    return s

def save_tex(latex_code, file_path):
    with open(file_path, 'w') as f:
        f.write('\documentclass{article}\n\n')
        f.write('\\usepackage{graphicx}\n\n')
        f.write('\\begin{document}\n\n')
        f.write(latex_code)
        f.write('\n\n\end{document}')

def generate_latex_image(
    file_path,
    width = None,
    height = None,
    scale = None
):
    options = []
    if width:
        options.append(f"width={width}")
    if height:
        options.append(f"height={height}")
    if scale:
        options.append(f"scale={scale}")
    
    options_str = ",".join(options)
    latex = f"\\includegraphics"
    if options:
        latex += f"[{options_str}]"
    latex += f"{{{file_path}}}"
    return latex
