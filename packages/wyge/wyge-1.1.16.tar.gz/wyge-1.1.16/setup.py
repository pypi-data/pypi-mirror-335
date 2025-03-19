from setuptools import setup, find_packages

setup(
    name="wyge",
    version="1.1.16",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=['openai', 'requests', 'numpy', 'pydantic[email]', 'langchain'], 
    author="Prudvi",
    author_email="prudhvisneha2003@gmail.com",
    description="A Python library for WYGE",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prudvireddyNS/vyzeai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.8",
)