from setuptools import setup, find_packages

setup(

    name="mood_recommender",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[],

    author="Hao Yang, Yukun Dong, Jess Liang, Yifan Zhang",
    author_email="hy2640@nyu.edu, yd2578@nyu.edu, jl13594@nyu.edu, yz9016@nyu.edu",


    description="A package to suggest activities based on mood.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
