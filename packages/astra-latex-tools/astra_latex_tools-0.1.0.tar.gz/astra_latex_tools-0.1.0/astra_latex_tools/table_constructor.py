import os

def write_in_file(text):
    """
    Записывает текст в файл 'output.tex' и выводит его в консоль.

    :param text: Текст для записи в файл.
    """
    with open('output.tex', 'a', encoding="utf-8") as f:
        f.write(text + '\n')
        print(text)


def fill_doc_starting(func):
    """
    Декоратор для очистки файла и добавления начальной информации LaTeX-документа.
    """
    def wrapped_func(*args, **kwargs):
        # Начальная информация для LaTeX-документа
        start_info = '''\\documentclass{article}
\\usepackage{graphicx} % Required for inserting images
'''
        # Очищаем файл, если он уже существует
        open('output.tex', 'w').close()

        write_in_file(start_info)
        func(*args, **kwargs)
    return wrapped_func


def add_custom_tag(tag):
    """
    Декоратор для добавления LaTeX-окружения с заданным тегом.

    :param tag: Название тега LaTeX-окружения (например, 'document', 'center', 'tabular').
    """
    def begin_end_template(func):
        def wrapped_func(*args, **kwargs):
            write_in_file(f'\\begin{{{tag}}}')
            func(*args, **kwargs)
            write_in_file(f'\\end{{{tag}}}')
        return wrapped_func
    return begin_end_template


@fill_doc_starting
@add_custom_tag('document')
@add_custom_tag('center')
@add_custom_tag('tabular')
def list_to_LaTex_table(matrix):
    """
    Преобразует двумерный список (матрицу) в LaTeX-таблицу и записывает её в файл.

    :param matrix: Двумерный список (список списков), представляющий таблицу.
    """
    n, m = len(matrix), len(matrix[0])
    write_in_file(f"{{{' '.join(['c'] * m)}}}")
    # Записываем строки таблицы
    for row in matrix:
        write_in_file(" & ".join(map(str, row)))
        write_in_file("\\\\")


@fill_doc_starting
@add_custom_tag('document')
def put_picture_to_LaTex(image_path):
    """
       Добавляет картинку в LaTeX-документ.
       :param image_path: Путь к изображению.
       """
    directory_path = os.path.dirname(image_path)
    if not directory_path:
        directory_path = '/'
    filename = os.path.basename(image_path)

    write_in_file(f"\\graphicspath{{{directory_path}}}")
    write_in_file(f"\includegraphics{{{filename}}}")
