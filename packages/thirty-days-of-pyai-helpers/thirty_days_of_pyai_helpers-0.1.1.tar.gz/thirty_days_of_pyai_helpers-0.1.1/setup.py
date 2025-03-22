from setuptools import setup, find_packages

setup(
    name="thirty-days-of-pyai-helpers",
    version="0.1.1",
    packages=find_packages(where=".", exclude=["tests"]),
    author="Witeout Codes",
    author_email="info@loveyourvecino.com",
    description="30 Days of AI with Python Course helper functions.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        "colorama==0.4.6"
    ],
    extras_require={
        "dev": [
            "pytest==7.1.2"
        ]
    },
    license="MIT",
    python_requires=">=3.6",  
)