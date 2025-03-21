print(f'Файл __init__.py в пакете {__name__}')

from .table_constructor import list_to_LaTex_table, put_picture_to_LaTex

__all__ = [
    list_to_LaTex_table,
    put_picture_to_LaTex
]