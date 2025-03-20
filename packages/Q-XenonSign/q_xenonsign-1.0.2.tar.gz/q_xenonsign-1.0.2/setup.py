from setuptools import setup, find_packages

setup(
    name="Q-XenonSign",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "requests",
        "pydantic",
        "pyngrok",
        "flask"
    ],
    author="Q-XenonSign",
    author_email="qxenonsign@gmail.com",
    description="Q-XenonSign library",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
