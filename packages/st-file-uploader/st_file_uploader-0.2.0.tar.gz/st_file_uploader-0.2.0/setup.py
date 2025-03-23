import setuptools

setuptools.setup(
    name="st_file_uploader",
    use_scm_version=True,
    author="Jerson Ruiz",
    author_email="jersonalvr@proton.me",
    description="A customizable file uploader component for Streamlit",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jersonalvr/st_file_uploader",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 1.26.0",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.39.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ],
    },
    setup_requires=["setuptools_scm"],
)
