from setuptools import setup, find_packages

setup(
    name="graphiteinterv2",
    version="0.3.5",
    description="A simple GUI framework with tkinter for creating interactive interfaces.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Leonardo",
    author_email="leo_nery@hotmail.com.br",
    packages=find_packages(),
    install_requires=[
        "Pillow" # Dependência que você está usando
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
