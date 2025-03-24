from setuptools import setup, find_packages

setup(
    name="mylibrary-wtitze",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    author="Tuo Nome",
    description="Una libreria per gestire veicoli in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wtitze/mylibrary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
