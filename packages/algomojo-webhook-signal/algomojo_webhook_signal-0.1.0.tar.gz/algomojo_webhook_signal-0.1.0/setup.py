from setuptools import setup, find_packages

setup(
    name="algomojo-webhook-signal",
    version="0.1.0",
    author="FinfoLab Technologies",
    author_email="support@algomojo.com",
    description="A Python library to place strategy signals via Algomojo webhook",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Finfolab-Technologies/Algomojo/algomojo-webhook-signal",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
