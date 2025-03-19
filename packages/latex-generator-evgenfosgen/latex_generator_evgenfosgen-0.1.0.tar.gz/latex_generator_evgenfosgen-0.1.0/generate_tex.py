from generator import generate_latex_text, generate_latex_image

# Данные для таблицы
table_data = [
    ["name", "years", "sity"],
    ["anna", 25, "moskow"],
    ["jon", 30, "spb"]
]

# Генерируем LaTeX-код
table_code = generate_latex_text(table_data)
image_code = generate_latex_image("fox.png")  # Файл картинки в той же папке

# Создаём полный LaTeX-документ
latex_document = f"""
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\begin{{document}}

{table_code}

{image_code}

\\end{{document}}
"""

# Записываем в файл output.tex
with open("output.tex", "w", encoding="utf-8") as file:
    file.write(latex_document)

print("✅ Файл output.tex успешно создан!")
