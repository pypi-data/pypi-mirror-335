from setuptools import setup, find_packages

setup(
    name="Hajime",
    version="1.3",
    packages=find_packages(),
    install_requires=['sqlalchemy', 'termcolor', 'websockets'],
    author="Franciszek Czajkowski",
    description="Lightweight Website Framework",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://Hajime.pythonanywhere.com",
    project_urls={
        "Source": "https://github.com/FCzajkowski/Hajime-Framework",
        "Documentation": "https://github.com/FCzajkowski/Hajime-Framework/blob/main/README.md"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)