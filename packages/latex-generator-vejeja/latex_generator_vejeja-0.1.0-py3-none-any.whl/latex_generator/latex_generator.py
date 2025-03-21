# src/latex_generator.py

def generate_table(data):
    """
    Принимает двойной список data и возвращает LaTeX-код таблицы.
    """
    if not data:
        return ""
    num_columns = len(data[0])
    col_spec = " | ".join(["l"] * num_columns)
    header = "\\begin{tabular}{" + col_spec + "}\n\\hline"
    rows = "\n\\hline\n".join(" & ".join(map(str, row)) + " \\\\" for row in data)
    footer = "\n\\hline\n\\end{tabular}"
    return header + "\n" + rows + footer

def generate_image(image_path, width="0.8\\textwidth"):
    """
    Возвращает строку LaTeX для вставки изображения.
    """
    return f"\\includegraphics[width={width}]{{{image_path}}}"

def generate_document(content):
    """
    Оборачивает переданный контент в минимальный документ LaTeX с поддержкой кириллицы.
    """
    header = (
        "\\documentclass{article}\n"
        "\\usepackage[utf8]{inputenc}\n"      # Кодировка UTF-8
        "\\usepackage[T2A]{fontenc}\n"         # Поддержка кириллицы
        "\\usepackage[russian]{babel}\n"       # Локализация для русского языка
        "\\usepackage{graphicx}\n"
        "\\begin{document}\n"
    )
    footer = "\n\\end{document}"
    return header + content + footer

