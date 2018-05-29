"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['FileSorter.py']
DATA_FILES = [('', ['locale'])]
OPTIONS = {'iconfile': './pic.icns'}

setup(
    version='0.2.6.5',
    description='File (mostly picture) sorting application/script',
    author='Konstantin Prilepin',
    author_email='deftonee@ya.ru',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
