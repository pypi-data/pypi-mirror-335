from setuptools import setup, find_packages

setup(
    name="agentsarcadia",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "langchain-openai>=0.3.9",
        "langgraph>=0.3.18",
        "python-dotenv>=1.0.1",
    ],
    author="seiji0906",
    author_email="yuto.miyashita.info@gmail.com",
    description="LangGraphによるワークフロー構築を支援するエージェントツール agentsarcadia",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/seiji0906/agentsarcadia",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
