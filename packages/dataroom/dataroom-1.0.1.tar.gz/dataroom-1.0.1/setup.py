import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dataroom",
    version="1.0.1",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="A powerful and easy-to-use data processing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "requests",
        "sqlalchemy",
        "scikit-learn",
    ],
)