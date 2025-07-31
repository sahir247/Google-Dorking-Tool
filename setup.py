from setuptools import setup

setup(
    name="GoogleDorkingTool",  # PyPI package name
    version="1.1",
    py_modules=["GoogleDorkingTool"],  # Must match your .py filename (without .py)
    author="Sahir Parvez",
    author_email="parvezsahir@gmail.com",
    description="A Python tool to automate advanced Google search dorking queries.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sahir247/Google-Dorking-Tool",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests"
    ],
    python_requires='>=3.6',
)
