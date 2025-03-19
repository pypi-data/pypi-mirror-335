from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fbtcore",
    version="2.0.1",
    author="Karesis",
    author_email="yangyifeng23@mails.ucas.ac.cn", 
    description="FBtree 2.0 - 高性能线程安全的树结构库",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Karesis/FBtree2.0",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "matplotlib",
    ],
)