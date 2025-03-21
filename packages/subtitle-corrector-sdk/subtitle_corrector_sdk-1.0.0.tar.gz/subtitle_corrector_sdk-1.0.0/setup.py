from setuptools import setup, find_packages

setup(
    name="subtitle_corrector_sdk",
    version="1.0.0",
    author="imuzhangy",
    author_email="imuzhangying@gmail.com",
    description="A package for correcting medical subtitles",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'subtitle_corrector_sdk': ['config.json', 'error_terms_library.json', 'prompt.txt'],
    },
    install_requires=[
        "requests",
        "json",
        "os",
        "shutil",
        "zipfile",
        "datetime",
        "logging",
        "re",
        "glob",
        "pkg_resources"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)