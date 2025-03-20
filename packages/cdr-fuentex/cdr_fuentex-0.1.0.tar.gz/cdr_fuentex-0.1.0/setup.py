from setuptools import setup, find_packages

setup(
    name='cdr_fuentex',  # Nombre del paquete en PyPI
    version='0.1.0',  
    packages=find_packages(),  
    install_requires=['pandas'],  # Dependencias
    author='Sergio Fuentes',
    author_email='fuentex.datalab@gmail.com',
    description='Librería para calcular el Coeficiente de Dispersión Relativa Fuentex (CDR-FX), útil para evaluar la dispersión relativa de variables en datasets.',
    url='https://github.com/FuentexDatalab/cdr_fuentex',  # URL de tu repositorio en GitHub
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    python_requires='>=3.7',  # Versión mínima de Python requerida
) 
