from setuptools import setup, find_packages

setup(
    name='simpledataquality',
    version='1.0.1',
    description='A package implement a basic data quelity check',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alan Medina',
    author_email='amedina.escom@hotmail.com',
    url='https://github.com/amedinag32/simpledataquality',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'greenlet==3.1.1',
        'mssqldbfacade==1.0.8',
        'numpy==1.24.4',
        'pandas==2.0.3',
        'pandasql==0.7.3',
        'pymssql==2.2.7',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.2',
        'six==1.17.0',
        'SQLAlchemy==2.0.36',
        'typing-extensions==4.12.2',
        'tzdata==2024.2',
    ],
)
