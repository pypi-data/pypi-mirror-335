from setuptools import setup, find_packages


setup(
    name="diffscope",
    version="0.1.0",
    author="doublelei",
    author_email="yutianleilei@outlook.com",
    description="Function-level git commit analysis tool",
    url="https://github.com/doublelei/DiffScope",
    project_urls={
        "Bug Tracker": "https://github.com/doublelei/DiffScope/issues",
        "Documentation": "https://diffscope.readthedocs.io",
        "Source Code": "https://github.com/doublelei/DiffScope",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "PyGithub>=2.1.1",
        "tree-sitter>=0.20.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "diffscope=diffscope.cli:main",
        ],
    },
    include_package_data=True,
    keywords='git, diff, analysis, code, function, commit',
    license="Apache License 2.0",
)
