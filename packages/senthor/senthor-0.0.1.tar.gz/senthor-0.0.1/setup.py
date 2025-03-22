from setuptools import setup, find_packages

setup(
    name="senthor",
    version="0.0.1",
    packages=find_packages(),
    description="Observability and evaluation layer for LLMs and RAG pipelines.",
    author="Seu Nome",
    author_email="seu@email.com",
    license="MIT",
    url="https://github.com/nelsonfrugeri-tech/senthor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)

