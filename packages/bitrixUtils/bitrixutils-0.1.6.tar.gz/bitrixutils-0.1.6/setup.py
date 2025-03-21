from setuptools import setup, find_packages

setup(
    name="bitrixUtils",
    version="0.1.6",
    author="Rafael Zelak Fernandes",
    author_email="rzf1503@gmail.com",
    description="Uma biblioteca para facilitar a integração com a API do Bitrix24",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/RafaelZelak/bitrixUtils.git",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
