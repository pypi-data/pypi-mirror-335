from setuptools import setup, find_packages

setup(
    name="loftyfamily",
    version="0.2",
    packages=find_packages(),
    install_requires=[],
    author="Oliver Fisher",
    description="A python library focused on providing up to date insights and information on Hazel Lofty",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Violevo/loftyfamily",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
