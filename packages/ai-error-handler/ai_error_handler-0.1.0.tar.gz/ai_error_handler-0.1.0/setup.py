from setuptools import setup, find_packages

setup(
    name="ai-error-handler",
    version="0.1.0",
    author="REDPENCIL",
    author_email="redpencil2025@gmail.com",
    description="A Python package for AI-based error handling.",
    long_description=open(r"C:\Users\unela\OneDrive\Desktop\ai_error_handler\ai_error_handler\README.md").read(),
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
