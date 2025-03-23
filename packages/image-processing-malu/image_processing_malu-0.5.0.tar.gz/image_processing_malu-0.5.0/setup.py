from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing_malu",
    version="0.5.0",
    author="Maria Luiza",
    author_email="romani.malu84@gmail.com",
    description="Pacote para processamento de imagens com histogram matching, similaridade estrutural e redimensionamento.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/malu-rm84/Package-dio",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)