import setuptools

setuptools.setup(
    name="st_file_uploader",
    version="0.1.0",
    author="Jerson Ruiz",
    author_email="jersonalvr@proton.me",
    description="A customizable file uploader component for Streamlit",
    long_description="""
    # Streamlit Custom File Uploader
    
    A customizable file uploader component for Streamlit that extends the original
    functionality by allowing customization of messages in different languages.
    """,
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
        "streamlit >= 1.18.0",
    ],
)