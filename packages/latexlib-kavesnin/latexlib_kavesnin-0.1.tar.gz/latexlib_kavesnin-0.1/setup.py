from setuptools import setup, find_packages

setup(
    name="latexlib_kavesnin",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Konstantin Vesnin",
    author_email="kavesnin@edu.hse.ru",
    description="A library for generating LaTeX tables and images.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kVesnin/latexlib_kavesnin",
)