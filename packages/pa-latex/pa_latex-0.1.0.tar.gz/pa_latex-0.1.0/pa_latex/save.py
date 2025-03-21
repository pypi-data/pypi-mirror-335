from pathlib import Path
from pdflatex import PDFLaTeX


def save_tex(latex: str, filename: str = "output", filepath: Path = Path("./artifacts")) -> Path:
    """
    Сохраняет LaTeX-код в .tex файл.

    :param latex: Строка с LaTeX-кодом.
    :param filename: Название файла без расширения (по умолчанию "output").
    :param filepath: Путь до директории, где будет сохранён файл (по умолчанию "./artifacts").
    :return: Путь до сохранненого файла.
    """
    # создаем если не существует
    filepath.mkdir(parents=True, exist_ok=True)

    full_path = filepath / f"{filename}.tex"

    with open(full_path, "w+", encoding="utf-8") as file:
        file.write(latex)

    print(f"Файл сохранён: {full_path}")
    return Path(full_path)



def save_pdf(tex_path: Path):
    """
    Сохраняет LaTeX-код в .pdf файл.
    """
    with open(tex_path.absolute(), 'rb') as f:
        pdfl = PDFLaTeX.from_binarystring(f.read(), 'my_file')
    pdf, log, cp = pdfl.create_pdf()

    # pdfl = PDFLaTeX.from_texfile(tex_path)
    # pdf, log, completed_process = pdfl.create_pdf(keep_pdf_file=True, keep_log_file=True)