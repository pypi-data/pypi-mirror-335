"""
Email Reverse Engine - Setup Script

Dit script installeert alle benodigde afhankelijkheden voor de Email Reverse Engine
"""

from setuptools import setup, find_packages
import os
import re

# Lees versie uit versiebestand of gebruik standaardversie
VERSION = '1.0.0'
try:
    with open('src/version.py', 'r') as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            VERSION = version_match.group(1)
except (FileNotFoundError, IOError):
    pass

# Lees README.md voor lange beschrijving
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except (FileNotFoundError, IOError):
    long_description = "Tool voor het achterhalen van emailadressen en het analyseren van online aanwezigheid"

# Kernvereisten (altijd nodig)
REQUIREMENTS = [
    "requests>=2.25.1",
    "dnspython>=2.1.0",
    "python-dotenv>=0.19.0",
    "email-validator>=1.1.3",
    "pyyaml>=6.0",
    "colorama>=0.4.4",
    "tqdm>=4.62.3",
]

# GUI vereisten (alleen nodig voor GUI-modus)
GUI_REQUIREMENTS = [
    "PyQt5>=5.15.4",
    "PyQt5-sip>=12.9.0",
    "PyQtChart>=5.15.4",
]

# Database vereisten (optioneel)
DB_REQUIREMENTS = [
    "SQLAlchemy>=1.4.23",
    "pymongo>=4.0.1",
]

setup(
    name="email_reverse_engine",
    version=VERSION,
    description="Tool voor het achterhalen van emailadressen en het analyseren van online aanwezigheid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Email Reverse Engine Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extras_require={
        'gui': GUI_REQUIREMENTS,
        'db': DB_REQUIREMENTS,
        'full': GUI_REQUIREMENTS + DB_REQUIREMENTS + [
            "beautifulsoup4>=4.9.3",
            "lxml>=4.6.3",
            "httpx>=0.23.0",
            "aiohttp>=3.8.1",
            "pandas>=1.3.3",
            "numpy>=1.21.2",
            "python-dateutil>=2.8.2",
            "openpyxl>=3.0.9",
            "jinja2>=3.0.1",
            "Markdown>=3.3.4",
            "pdfkit>=1.0.0",
        ],
        'dev': [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
            "pytest-qt>=4.0.2",
            "black>=21.8b0",
            "flake8>=3.9.2",
            "mypy>=0.910",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "email-reverse-engine=src.run_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Security",
    ],
)
