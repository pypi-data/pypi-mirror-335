from setuptools import setup, find_packages

setup(
    name="TerminaltextTools_ARTariqDev",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "textual",
        "python-docx",
        "chardet",
    ],
    entry_points={
        "console_scripts": [
            "textSummarizer = textSummarizer.main:main"
        ]
    },
    author="Abdur Rehman Tariq",
    description="A CLI tool to summarize text files using GPT-3.5-turbo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
