from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from README.md
readme_path = Path(__file__).parent / "README.md"
with readme_path.open("r", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="encrypt_data",
    version="0.4",
    packages=find_packages(),
    install_requires=["cryptography", "rsa"],
    description="Hybrid Encryption & Decryption with Minimal Efforts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Manthan Phadse",
    author_email="manthan.phadse04@gmail.com",
    url="https://github.com/Manthan-04/encrypt_data.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
