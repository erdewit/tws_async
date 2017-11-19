import os
import sys
from setuptools import setup
from codecs import open

if sys.version_info < (3, 5, 0):
    raise RuntimeError("tws_async requires Python 3.5.0+")

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tws_async',
    version='0.5.7',
    description=('Use the Interactive Brokers API (IBAPI) asynchonously'
            'with asyncio or PyQt5'),
    long_description=long_description,
    url='https://github.com/erdewit/tws_async',
    author='Ewald R. de Wit',
    author_email='ewald.de.wit@gmail.com',
    license='Freeware',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: Freeware',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='ibapi asyncio qt pyqt pyqt5 jupyter interactive brokers async',
    packages=['tws_async'],
    install_requires=['PyQt5', 'quamash', 'pytz', 'jupyter', 'numpy',
       'pandas', 'seaborn'],
    data_files=[
        ('samples', ['samples/histrequester_demo.py']),
        ('samples', ['samples/tickstreamer_demo.py']),
        ('samples', ['samples/tws.ipynb']),
        ],
    zip_safe=False,
)
