from generator import generate_latex_text, generate_latex_image

table_data = [
    ["name", "years", "sity"],
    ["anna", 25, "moskow"],
    ["jon", 30, "spb"]
]


table_code = generate_latex_text(table_data)
image_code = generate_latex_image("fox.png")


latex_document = f"""
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\begin{{document}}

{table_code}

{image_code}

\\end{{document}}
"""


with open("output.tex", "w", encoding="utf-8") as file:
    file.write(latex_document)

print("✅ файл output.tex успешно создан!")
