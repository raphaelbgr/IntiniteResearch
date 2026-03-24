"""Setup script for Infinite Research system."""
from setuptools import setup, find_packages

setup(
    name="infinite-research",
    version="1.0.0",
    description="Autonomous research system with infinite refinement using Agno agents",
    author="Your Name",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "agno>=3.0.0",
        "openai>=1.0.0",
        "pgvector>=0.3.0",
        "psycopg2-binary>=2.9.0",
        "sqlite-vec>=0.1.0",
        "aiofiles>=23.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "pypdf>=4.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "sentence-transformers>=2.5.0",
        "tqdm>=4.66.0",
        "rich>=13.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "infinite-research=research_orchestrator:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
