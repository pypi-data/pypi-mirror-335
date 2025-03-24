from setuptools import setup

setup(
    name="richui",
    version="0.0.2",
    packages=["richui"],
    install_requires=["rich"],
    author="Moh Iqbal Hidayat",
    author_email="iqbalmh18.dev@gmail.com",
    description="An interactive command-line UI module built on top of Rich for customizable UI components.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/richui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["rich", "richui", "cli", "ui", "terminal", "interactive"],
    python_requires=">=3.7",
)