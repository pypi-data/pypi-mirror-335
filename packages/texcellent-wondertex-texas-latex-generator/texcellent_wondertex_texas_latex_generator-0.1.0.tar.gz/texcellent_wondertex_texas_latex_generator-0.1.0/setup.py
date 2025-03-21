from setuptools import setup, find_packages

setup(
    name="texcellent_wondertex_texas_latex_generator",
    version="0.1.0",
    author="Kalinin Ivan",
    author_email="jeck5ivk@gmail.com",
    description="A library to generate LaTeX code for tables and images.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jeck5iv/pythonHW",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license="MIT",
)
