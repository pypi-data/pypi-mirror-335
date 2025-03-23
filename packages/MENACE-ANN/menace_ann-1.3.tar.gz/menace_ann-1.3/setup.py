from setuptools import setup


with open("README.md", 'r') as readme:
    long_description = readme.read()



setup(
    name="MENACE_ANN",
    version="1.3",
    description="An implementation of the first Noughts and Crosses Artificial Neural Network, made with matchboxes and MENACE. Final version.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LordUbuntu/MENACE",
    keywords=["python", "tic tac toe", "noughts and crosses", "Matchbox Enabled Noughts and Crosses Engine", "MENACE", "Neural Network", "AI"],
    license="MIT",
    author="Jacobus Burger",
    author_email="therealjacoburger@gmail.com",
    packages=["menace_ann"],
    extras_require={
        "dev": ["pytest>=7.2", "twine>=4.0.2"],
    },
    python_requires=">=3.10",
    platforms=["any"],
    py_modules=["menace_ann"],
    entry_points={
        "console_scripts": ["menace_ann=menace_ann.__main__:main"]
    },
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
    ]
)
