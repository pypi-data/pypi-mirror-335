from setuptools import setup, find_packages

setup(
    name="Infinity_AI",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "g4f"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Infinity AI - AI Chat Library for free!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Infinity_AI",  # Change this to your GitHub repo
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
