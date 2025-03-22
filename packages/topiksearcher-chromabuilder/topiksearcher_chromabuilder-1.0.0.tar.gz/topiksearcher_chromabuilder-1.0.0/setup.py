from setuptools import setup, find_packages
setup(
    name="topiksearcher_chromabuilder",
    version="1.0.0",
    description="Topik-aware semantic search untuk dokumen hukum berbasis vectorstore, dan pembuatan CrhomaDB dari dokumen humum",
    author="Agus Afiantara",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-huggingface",
        "langchain-chroma",
        "rapidfuzz",
        "numpy",
        "fitz",
    ],
     python_requires=">=3.8"
)
