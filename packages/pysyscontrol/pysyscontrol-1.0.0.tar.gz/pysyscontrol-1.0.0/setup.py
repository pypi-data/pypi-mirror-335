from setuptools import setup, find_packages

setup(
  name="pysyscontrol",
  version="1.0.0",
  author="Shagedoorn1",
  author_email="svenhagedoorn@gmail.com",
  description="A Python package for Control Systems Analysis",
  license_files=["LICENSE"],
  long_description=open("README.md").read(),
  url="https://github.com/Shagedoorn1/PyControl",
  long_description_content_type="text/markdown",
  packages=find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.12"
)