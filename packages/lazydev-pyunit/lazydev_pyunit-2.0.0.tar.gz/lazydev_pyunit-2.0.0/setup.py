from setuptools import setup, find_packages

setup(
    name="lazydev_pyunit",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[],
    author="Mahmoud Shehata, Syed Naqvi, Brandon Morales, David Yu",
    author_email="mss9253@nyu.edu, san7576@nyu.edu, bam9516@nyu.edu, dy2262@nyu.edu,",
    description="A package for lazy developers so that they can write commit messages, write pull request titles, generate random excuses, and other assorted laziness without thinking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/software-students-spring2025/3-python-package-pyunit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
