from setuptools import setup, find_packages

setup(
    name='curses-colors',
    version='0.1.0',
    author='xlebore3o4ka',
    author_email='xlebore3o4ka@gmail.com',
    description='`curses-colors` is a Python module that provides a simple interface for managing color pairs in a terminal using the `curses` library.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/xlebore3o4ka/curses-colors/tree/main',  # URL вашего репозитория
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)