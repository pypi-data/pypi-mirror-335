from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()


long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name='analytic_workspace_client',
    version='1.33.0',

    description='Библиотека для подключения к Analytic Workspace',
    long_description=long_description,
    long_description_content_type="text/markdown",


    author='Analytic Workspace',
    author_email='aw_help@analyticworkspace.ru',
    url='https://analyticworkspace.ru/',

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],

    python_requires='>=3.10,<4',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),

    install_requires=[
        'python-dotenv>=1.0,<1.1',
        'httpx>=0.25,<1.0',
        'pandas',
        'pydantic>=2.0',
        'colorama>=0.4,<0.5',
        'pyjwt==2.10.1',
    ],

    extras_require={
        'dev': ['pyspark==3.5.1', 'pytest>=8.2,<8.3', 'pyparsing>=3.2,<3.3', 'requests>=2.32,<2.33'],
        'ml': ['mlflow==2.14.3']
    },
    
    setup_requires=['wheel'],  
)
