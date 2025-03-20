from setuptools import setup, find_packages
from Cython.Build import cythonize
from setuptools.extension import Extension
import glob
import os

# Cython을 적용할 파일 찾기
source_files = glob.glob("fourtest/*.py") + [r"C:\Users\ekgml\lim\QXenonSign\qxenonsign\core.c"]

# 확장 모듈 설정
extensions = [
    Extension(
        name=os.path.splitext(os.path.basename(file))[0],
        sources=[file],
    )
    for file in source_files
]

setup(
    name="Q-XenonSign",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "requests",
        "pydantic",
        "pyngrok",
        "flask"
        
    ],
    ext_modules=cythonize(extensions, language_level="3"),
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