from setuptools import setup,find_packages
from pathlib import Path

setup(
   name='adpro-video-ferramentas-Adbreyk-24-ad',
   version=1.0,
   description='Este pacote irá fornecer ferramentas de processamento de vídeo',
   long_description=Path('README.md').read_text(),
   author='Adbreyk',
   author_email='2333adbreyk@gmail.com',
   keywords=['Camera','Vídeo','processamento'],
   packages=find_packages()
)
