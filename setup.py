from setuptools import setup

setup(
    name="magicparse",
    version="0.9.1",
    description="Declarative parser",
    author="ZG",
    author_email="dev@zero-gachis.com",
    python_requires=">=3.9.0",
    url="https://github.com/ZeroGachis/magicparse",
    packages=[
        "magicparse",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "pytest",
        ]
    },
)
