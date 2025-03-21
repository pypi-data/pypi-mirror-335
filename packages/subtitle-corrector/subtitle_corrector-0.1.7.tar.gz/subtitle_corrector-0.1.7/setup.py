from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="subtitle_corrector",
    version="0.1.7",
    author="imuzhangy",
    author_email="imuzhangying@gmail.com",
    description="A package for correcting medical subtitles",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'subtitle_corrector': ['config.json', 'error_terms_library.json'],
    },
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    ext_modules=cythonize("subtitle_corrector/subtitle_corrector.pyx"),
)