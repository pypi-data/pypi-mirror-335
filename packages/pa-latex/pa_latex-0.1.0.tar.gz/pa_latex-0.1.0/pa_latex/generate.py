from typing import Tuple, List, Optional

def generate_table(column_names: List[str], data: List[List]) -> str:
    """
    Функция для генерации LaTeX-кода для таблицы на основе двойного списка.

    :param data: Двойной список, где каждый внутренний список представляет строку таблицы.
    :return: Строка с отформатированным LaTeX-кодом таблицы.
    :raises ValueError: Если входные данные пусты, не являются списком списков или если длины списков различаются.
    """

    num_columns = len(column_names)
    # проверить валидность входящих данных файла
    if not data or not all(isinstance(row, list) and (len(row) == num_columns) for row in data):
        raise ValueError("Check your data! It may be not list of lists or length of lists are not the same.")
        

    start_table = "\\begin{center}\n" \
                    + "\\begin{tabular}" \
                    + f"{{||{'c ' * num_columns}||}}\n" \
                    + "\\hline\n" \
                    + f"{' & '.join(column_names)} \\\\\n"

    end_table = "\\end{tabular}\n\\end{center}\n"
    line_pattern = "\\hline\n" + r"{0} \\" + "\n"

    table_body = ""
    for row in data:
        ltx_row = " & ".join(map(str, row))
        line = line_pattern.format(ltx_row)
        table_body += line

    table_body += "\\hline\n"
    return start_table + table_body + end_table


def get_document_begin_end(title: Optional[str] = None) -> Tuple[str, str]:
    """
    Генерирует начало и конец LaTeX-документа.

    Функция возвращает кортеж из двух строк:
    1. Начало LaTeX-документа, включая объявление класса документа (article),
       подключение пакета graphicx и (опционально) заголовок документа.
    2. Конец LaTeX-документа.

    :param title: Опциональный заголовок документа. Если передан, добавляется в начало документа.
    :return: Кортеж из двух строк: (начало документа, конец документа).

    """
    begin = """\\documentclass{article}
            \\usepackage{graphicx}
            
            \\begin{document}"""
            
    
    if title:
        begin += f"\\title{{{title}}}\n"

    end = "\\end{document}"
    return begin, end


def generate_image(filename, scale=1.0):
    """
    Функция для генерации LaTeX-кода для вставки изображения.

    :param filename: Название файла изображения (с расширением)
    :param scale: Масштаб изображения (по умолчанию 1.0)
    :return: Строка с отформатированным LaTeX
    """
    latex_code = f"""
\\begin{{figure}}[h!]
    \\centering
    \\includegraphics[scale={scale}]{{{filename}}}
    \\caption{{}}
    \\label{{fig:{filename.split('.')[0]}}}
\\end{{figure}}
"""
    return latex_code

