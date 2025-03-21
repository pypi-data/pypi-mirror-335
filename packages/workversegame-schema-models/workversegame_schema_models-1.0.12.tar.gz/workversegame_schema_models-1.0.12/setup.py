from setuptools import setup, find_packages

setup(
    name="workversegame_schema_models",
    version="1.0.12",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="Auto-generated Python database models from JSON schemas",
    author="WorkverseGame",
    author_email="your-email@example.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pydantic>=1.8.0",
    ],
)
