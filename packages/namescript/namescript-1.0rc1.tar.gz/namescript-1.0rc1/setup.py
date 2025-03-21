from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="namescript",
    version="1.0c1",
    author="AkzDev",
    author_email="email@anda.com",
    description="Bahasa pemrograman NameScript dengan sintaks Indonesia",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://akuzz.my.id/NameScript",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ns=namescript.commands:main',
        ],
    },
    python_requires='>=3.6',
    license="MIT",
)