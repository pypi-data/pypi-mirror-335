from setuptools import setup, find_packages

setup(
    name='dbS3',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'boto3==1.28.25',
        'tinydb==4.8.0'
    ],
    include_package_data=True,
    author='Wanderson Viana',
    author_email='wanderson.viana@minervafoods.com',
    description='Pequeno banco de dados que armazena informações no S3 usando TinyDB.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/wandersomMv/dbS3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
