from setuptools import setup, find_packages

setup(
    name="dxcord",  
    version="0.1.0",  
    packages=find_packages(),  
    install_requires=[
        "requests",
        "colorama",
    ],
    author="s0rdeal",  
    author_email="sordealpro@gmail.com",  
    description="Discord API Wrapper",  
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/s0rdeal/dxcord",
    license="MIT",  # Type de licence (MIT, GPL, etc.)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",  
)
