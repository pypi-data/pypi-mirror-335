# setup.py

from setuptools import setup, find_packages

setup(
    name="super_latex_tools",
    version="0.1.0",
    author="cormeum",
    author_email="armus2812@gmail.com",
    description="A library for generating LaTeX tables and images.",
    #long_description=open("README.md").read(),
    #long_description_content_type="text/markdown",
    #url="https://github.com/yourusername/latex_library",  # Замените на ваш репозиторий
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)