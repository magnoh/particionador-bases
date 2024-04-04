import os
import PyInstaller.__main__

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(BASE_DIR, 'atualizar-pares-de-setas-em-circulo.png')

PyInstaller.__main__.run([
    'particionamento.py',
    '--onefile',
    '--noconsole',
    '--name',
    'particionador de bases',
    '--clean',
    '--icon',
    'corte.ico',
    '--add-data',
    f'{image_path};.'
])