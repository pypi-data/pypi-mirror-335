def generate_latex_text(data):
    num_columns = len(data[0])

    # Используем обычные "c" вместо "p{4cm}"
    column_format = "|".join(["c"] * num_columns)

    latex_code = f"\\begin{{tabular}}{{|{column_format}|}}\n\\hline\n"

    # Добавляем заголовки таблицы
    headers = " & ".join(map(str, data[0]))
    latex_code += headers + " \\\\\n\\hline\n"

    # Добавляем данные (вторую и последующие строки)
    for row in data[1:]:
        row_data = " & ".join(map(str, row))
        latex_code += row_data + " \\\\\n\\hline\n"

    latex_code += "\\end{tabular}\n"
    return latex_code


def generate_latex_image(image_path, caption="pic"):
    return f"""
    \\begin{{figure}}[h]
        \\centering
        \\includegraphics[width=0.8\\textwidth]{{{image_path}}}
        \\caption{{{caption}}}
        \\label{{fig:image}}
    \\end{{figure}}
    """
