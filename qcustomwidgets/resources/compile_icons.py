
from pathlib import Path
from os import sep
import subprocess


def svg_path():
    return Path(__file__).parents[1] / 'assets' / 'svg'


def png_path():
    return Path(__file__).parents[1] / 'assets' / 'png'


def collect_files() -> None:
    for filename, ext in [('icons', 'svg'), ('images', 'png')]:
        with open(Path(__file__).parent / f'{filename}.qrc', 'w') as f:
            f.write('<!DOCTYPE RCC>\n<RCC version="1.0">\n')
            f.write(f'<qresource prefix="{ext}">\n')
            for file in (Path(__file__).parents[1] / 'assets' / ext).glob(f'*.{ext}'):
                f.write(f'<file alias="{file.stem}">..{sep}{file.relative_to(Path(__file__).parents[1])}</file>\n')
            f.write('</qresource>\n')
            f.write('</RCC>\n')


def compile_qrc():
    for filename in ['icons', 'images']:
        qrc_path = Path(__file__).parent / f'{filename}.qrc'
        resource_path = Path(__file__).parent / f'{filename}.py'
        subprocess.run(['pyside6-rcc', qrc_path, '-o', resource_path])

        old = 'from PySide6 import QtCore'
        new = (
        'try:\n'
        '    from PySide6 import QtCore\n'
        'except ImportError:\n'
        '    from PyQt6 import QtCore'
        )
        with open(resource_path, 'r', encoding='utf-8') as file:
            content = file.read()
            content = content.replace(old, new)
        with open(resource_path, 'w', encoding='utf-8') as file:
            file.write(content)



if __name__ == '__main__':
    collect_files()
    compile_qrc()