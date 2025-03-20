
from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "FlowScript is a Python package for workflow scheduling and execution."

setup(
    name="FlowScript",        
    version="0.1.0",
    packages=find_packages(),     
    install_requires=[
        # 'requests>=2.25.1',
    ],
    author="M.Sridhar",
    author_email="mailtosridhar01@gmail.com",
    description="A test automation package for workflow scheduling and execution.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sridhar-mani/test-automation",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            # "test-automation = test_automation.main:main",
        ],
    },
)
