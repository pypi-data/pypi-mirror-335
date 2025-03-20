from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="TxtToImg",  # Name of your package
    version="0.1.1",  # Version of your package
    author="Nelvin Jaziel Marquez (Jaziel Developer)",  # Your name
    author_email="nelvinjazieldeveloper@gmail.com",  # Your email
    description="A Python library to create images with customizable text overlays.",  # Short description
    long_description=long_description,  # Long description from README.md
    long_description_content_type="text/markdown",  # Type of long description
    url="https://github.com/nelvinjazieldeveloper/txt2img",  # URL to your project repository
    packages=find_packages(),  # Automatically find packages in the project
    install_requires=[  # List of dependencies
        "opencv-python>=4.5.5",
        "numpy>=1.21.0",
        "requests>=2.26.0",
    ],
    classifiers=[  # Metadata about your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
)