from setuptools import setup, find_packages

setup(
    name='panlit',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.0.0',
    ],
    author='Pan Lancer',
    description='A Python package that depends on Streamlit'
)
