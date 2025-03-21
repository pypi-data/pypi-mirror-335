from setuptools import setup, find_packages

setup(
    name="rtv_solver",
    version="0.1.4",
    description="A solver for real-time vehicle routing problems",
    author="Danushka Edirimanna",
    author_email="ke233@cornell.edu",
    license="MIT",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(include=["rtv_solver"]),  # Matches `find = { include = ["rtv_solver"] }`
    install_requires=[],  # No dependencies for now
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
