from setuptools import setup, find_packages

setup(
    name="chatsynth_vanshajr",
    version="0.1.0",
    description="A library for creating and deploying chatbots with FAISS and GitHub integration for the ChatSynth app: https://chatsynth.streamlit.app.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Vanshaj Raghuvanshi",
    author_email="vanshajraghuvanshi@gmail.com",
    url="https://github.com/VanshajR/chatsynth_vanshajr", 
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "langchain",
        "langchain-community",
        "langchain-groq",
        "langchain-huggingface",
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License", 
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)