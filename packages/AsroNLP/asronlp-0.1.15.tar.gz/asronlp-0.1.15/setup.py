from setuptools import setup, find_packages

setup(
    name='AsroNLP',
    version='0.1.15',
    author='Asro',
    author_email='info@raharja.info',
    description='Paket NLP untuk pengolahan teks Bahasa Indonesia',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/asroharun6/AsroNLP',
    packages=find_packages(),
    package_data={'asro_nlp': ['data/*']},
    include_package_data=True,
    install_requires=[
        'pandas',
        'nltk',
        'openpyxl'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
