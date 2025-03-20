from setuptools import setup, find_packages

# Read long description from README.md safely
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-error-handler",
    version="0.1.1",
    author="REDPENCIL",
    author_email="redpencil2025@gmail.com",
    description="A Python package for AI-based error handling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Avi-lapulga/ai-error-handler",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python",  # Add dependencies
        "fastapi",
        "uvicorn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
