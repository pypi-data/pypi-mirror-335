from setuptools import setup, find_packages

setup(
    name="subtitle_corrector_sdk",
    version="0.1.0",
    author="imuzhangy",
    author_email="imuzhangying@gmail.com",
    description="A package for correcting medical subtitles",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "psutil>=5.8.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)