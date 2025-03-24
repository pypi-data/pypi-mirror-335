from setuptools import setup, find_packages

setup(
    name="sheetsmart",
    version="1.1.0",
    author="Bhuvanesh M",
    author_email="bhuvaneshm.developer@gmail.com",
    description="SheetSmart: Intelligent spreadsheet management tool for enhanced data handling and automation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bhuvanesh-m-dev/sheetsmart",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPLv3 or Sheetsmart Commercial License",
    python_requires=">=3.6",
    project_urls={
        "Portfolio": "https://bhuvaneshm.in",
        "LinkedIn": "https://www.linkedin.com/in/bhuvaneshm-developer",
        "GitHub Repository": "https://github.com/bhuvanesh-m-dev",
    },
)
