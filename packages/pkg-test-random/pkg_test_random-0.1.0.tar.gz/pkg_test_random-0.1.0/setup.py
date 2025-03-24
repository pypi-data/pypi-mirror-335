from setuptools import setup, find_packages

setup(
    name="pkg_test_random",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Ajay Garad",
    author_email="gajay2696@gmail.com",
    description="A simple example package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AjayGarad/py_pkg_project",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
