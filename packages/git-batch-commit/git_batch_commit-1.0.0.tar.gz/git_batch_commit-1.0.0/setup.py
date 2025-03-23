from setuptools import setup, find_packages

setup(
    name="git-batch-commit",
    version="1.0.0",
    author="Vaishal",
    description="A powerful Git batch commit tool by Vaishal.",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "git-batch-commit=git_batch_commit.main:batch_commit"
        ]
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
