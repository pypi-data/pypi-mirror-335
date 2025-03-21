from generate import generate_table, generate_image, get_document_begin_end
from save import save_tex, save_pdf


if __name__ == '__main__':

    cols = ["Header 1", "Header 2", "Header 3"]
    data = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    filename = "5money.jpg"

    # генерация и сборка документа:    
    begin, end = get_document_begin_end()
    table = generate_table(cols, data)
    image = generate_image(filename, 0.1)
    tex = begin + image + table + end
    tex_path = save_tex(tex)
    save_pdf(tex_path)
