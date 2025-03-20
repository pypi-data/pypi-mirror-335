from setuptools import setup, find_packages

setup(
    name='bcampe',
    version='0.95',
    packages=find_packages(),
    install_requires=[
        'wheel',
        'setuptools',
        'streamlit',
        'plotly',
        'matplotlib',
        'pandas'
    ],  
    author='brunocampello',
    author_email='alancampiello@gmail.com',
    description='Funções, estilos e gráficos utilizados na construção de soluções de BI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    package_data={
        'bcampe.estilos': ['styles.css'],  # Inclui o arquivo CSS no pacote
    },
    include_package_data=True,  
    
)
