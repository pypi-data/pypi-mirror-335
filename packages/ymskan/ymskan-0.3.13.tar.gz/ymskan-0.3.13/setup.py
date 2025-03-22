import setuptools

# Load the long_description from README.md
with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ymskan",
    version="0.3.13",
    author="yyyyy",
    author_email="226000@qq.com",
    description="Ko9tworks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={  
        'pykan': [
            'figures/lock.png',
            'assets/img/sum_symbol.png',
            'assets/img/mult_symbol.png',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
