from setuptools import setup, find_packages

setup(
    name='miracle-helper',
    version='0.0.30',
    description='MIRACLE.cowf LangChain Helper',
    author='MIRACLE.cowf',
    author_email='miracle.cowf@gmail.com',
    url='https://github.com/MIRACLE-cowf/Powerful-Auto-Researcher.git',
    install_requires=[
        'langchain >= 0.3.21',
        'langchain-anthropic >= 0.3.10',
        'langchain-openai >= 0.3.9',
        'langchain-core >= 0.3.47',
        'langchain-voyageai >= 0.1.4',
        'langgraph >= 0.3.18',
        'async-timeout == 4.0.3',
        'pydantic == 2.10.6',
        'pydantic-core == 2.27.2'
    ],
    packages=find_packages(exclude=[]),
    keywords=['miracle', 'miracle.cowf', 'custom langchain', 'langchain helper', 'pypi'],
    python_requires='>=3.10',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
