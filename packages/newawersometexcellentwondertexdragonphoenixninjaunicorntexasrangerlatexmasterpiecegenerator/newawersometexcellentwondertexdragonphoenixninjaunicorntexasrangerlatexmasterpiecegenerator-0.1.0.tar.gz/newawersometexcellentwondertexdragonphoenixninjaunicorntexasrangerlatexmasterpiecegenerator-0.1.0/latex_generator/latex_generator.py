from functools import reduce

def generate_latex_table(data):
    """
    Генерирует строку с LaTeX-кодом таблицы.
    
    :param data: Двойной список с данными (матрица).
    :return: Строка с валидным кодом LaTeX-таблицы.
    """
    def validate_data(data):
        if not data or not all(isinstance(row, list) for row in data):
            raise ValueError("Неверный формат данных. Ожидается список списков.")
        return data

    def generate_col_format(num_cols):
        return "| " + " | ".join(["c"] * num_cols) + " |"

    def generate_rows(data):
        return map(lambda row: " & ".join(map(str, row)) + " \\\\\n\\hline\n", data)

    def build_table(col_format, rows):
        table_header = (
            "\\begin{table}[h]\n\\centering\n"
            f"\\begin{{tabular}}{{ {col_format} }}\n\\hline\n"
        )
        table_body = reduce(lambda acc, row: acc + row, rows, "")
        table_footer = (
            "\\end{tabular}\n"
            "\\label{tab:example}\n"
            "\\end{table}\n"
        )
        return table_header + table_body + table_footer

    return build_table(
        generate_col_format(len(validate_data(data)[0])),
        generate_rows(validate_data(data))
    )

def generate_latex_image(image_path, width="0.5\\textwidth"):
    """
    Генерирует LaTeX-код для вставки изображения.

    :param image_path: Путь к изображению (относительный).
    :param width: Ширина изображения в LaTeX.
    :return: Строка с LaTeX-кодом для вставки картинки.
    """
    return f"""
\\begin{{figure}}[h]
    \\centering
    \\includegraphics[width={width}]{{{image_path}}}
    \\label{{fig:example}}
\\end{{figure}}
"""

def generate_latex(data=None, image_path=None):
    """
    Генерирует полный LaTeX-документ с таблицей и/или изображением.

    :param data: Двумерный массив данных для таблицы (по умолчанию None).
    :param image_path: Путь к изображению (по умолчанию None).
    :return: Полный LaTeX-документ в виде строки.
    """
    latex_content = "\\documentclass{article}\n\\usepackage{booktabs}\n\\usepackage{graphicx}\n\\begin{document}\n"

    if data is not None:
        latex_content += generate_latex_table(data) + "\n"

    if image_path is not None:
        latex_content += generate_latex_image(image_path) + "\n"

    latex_content += "\\end{document}"

    return latex_content