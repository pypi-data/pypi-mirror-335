from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="s2_ai_tools",
    version="1.0.6",
    description="Singlestore tools definitions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Singlestore",
    author_email="support@singlestore.com",
    url="https://github.com/singlestore-labs/singlestore-ai-tools",
    packages=find_packages(),
    install_requires=[
        "requests",
        "singlestoredb",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
