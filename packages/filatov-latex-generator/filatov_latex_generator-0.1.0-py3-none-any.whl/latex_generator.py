def generate_latex_table(data):
    if not data or not all(isinstance(row, list) for row in data):
        raise "Неверный формат данных для таблицы"
    
    columns_number = len(data[0])

    columns_format = "|" + "|".join(["c"] * columns_number) + "|"

    lines = [
        r"\begin{tabular}{" + columns_format + r"}",
        r"\hline"
    ]

    for row in data:
        row_str = " & ".join(str(cell) for cell in row) + r" \\"
        lines.append(row_str)
        lines.append(r"\hline")

    lines.append(r"\end{tabular}")
    return "\n".join(lines)

def generate_latex_picture(image_path, width, caption=None, label=None):
    figure_code = [
        r"\begin{figure}",
        r"\centering",
        rf"\includegraphics[width={width}\linewidth]{{{image_path}}}",
    ]
    if caption:
        figure_code.append(rf"\caption{{{caption}}}")
    if label:
        figure_code.append(rf"\label{{{label}}}")
    figure_code.append(r"\end{figure}")

    return "\n".join(figure_code)
