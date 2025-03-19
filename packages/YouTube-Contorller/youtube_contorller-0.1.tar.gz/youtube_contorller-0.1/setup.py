from setuptools import setup, find_packages

setup(
    name='YouTube_Contorller',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',  # Указываем зависимость от selenium
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
)
