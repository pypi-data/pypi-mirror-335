from setuptools import setup, find_packages

setup(
    name="falcon-arch",
    version="0.0.2",
    description="FalconArch is a lightweight and modular library that provides a base structure for developing applications with Flask.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Célio Junior",
    author_email="profissional.celiojunior@outlook.com",
    url="https://github.com/celiovmjr/falcon-arch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'Flask>=3.0.0',
        'waitress>=3.0.2',
    ],
)
