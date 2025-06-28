from setuptools import setup, find_packages

setup(
    name="brainfish-python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-chess>=1.0.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "mypy>=0.910",
            "flake8>=3.9.0",
        ]
    },
    author="BlackBoxAI",
    description="Python orchestration layer for BrainFish chess engine",
    python_requires=">=3.8",
)
