from setuptools import setup, find_packages

setup(
    name="failsafe",
    version="1.0.1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    description="A lightweight, simpler, more pythonic testing framework",
    author="TheOmniOnic",
    license="MIT",
    packages=find_packages(where="."), 
    include_package_data=True, 
    url="https://github.com/TheOmniOnic/failsafe",
    classifiers=[  
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
