from setuptools import setup, find_packages

# Leer el contenido del README.md para usarlo como descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cdr_fuentex",
    version="0.1.1",  # nueva version con descripcion
    author="FuentexDatalab",
    author_email="fuentex.datalab@gmail.com",
    description="Librería para calcular el Coeficiente de Dispersión Relativa Fuentex (CDR-FX).",
    long_description=long_description,
    long_description_content_type="text/markdown",  # que se tome como texto
    url="https://github.com/FuentexDatalab/cdr_fuentex",
    packages=find_packages(),
    install_requires=["pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
