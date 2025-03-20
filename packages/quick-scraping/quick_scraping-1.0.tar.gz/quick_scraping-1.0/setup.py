"""
Setup para a biblioteca quick-scraping.
"""

from setuptools import setup, find_packages
import os

# Lê o conteúdo do arquivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Requisitos de instalação
install_requires = [
    "beautifulsoup4>=4.9.0",
    "selenium>=4.0.0",
    "requests>=2.25.0",
    "lxml>=4.6.0",  # Parser alternativo para BeautifulSoup
]

# Requisitos opcionais
extras_require = {
    'dev': [
        'pytest>=6.0.0',
        'black',
        'flake8',
        'mypy',
    ],
    'docs': [
        'sphinx>=4.0.0',
        'sphinx-rtd-theme',
    ],
}

setup(
    name="quick-scraping",
    version="1.0",
    author="Bruno Sardou",
    author_email="bruno.sardou@outlook.com",
    description="Toolkit para web scraping combinando Selenium e BeautifulSoup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bruno-sardou/quick-scraping",
    project_urls={
        "Bug Tracker": "https://github.com/bruno-sardou/quick-scraping/issues",
        "Documentation": "https://quick-scraping.readthedocs.io/",
        "Source Code": "https://github.com/bruno-sardou/quick-scraping",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="web scraping, selenium, beautifulsoup, automation, html, parsing, extraction",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "quick-scraper=quick_scraping.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)