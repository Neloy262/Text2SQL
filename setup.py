"""
Setup configuration for the Natural Language to SQL application.
"""
from setuptools import setup, find_packages

setup(
    name="natural-language-to-sql",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.5.0",
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "datasets>=2.14.0",
        "faiss-cpu>=1.7.0",
        "sentence-transformers>=2.2.0",
        "accelerate>=0.20.0",
        "sqlalchemy>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "nsql=natural_language_to_sql.cli.main:main",
        ],
    },
)