from setuptools import setup

setup(
    name="GoogleDorkingTool",
    version="1.1",
    description="Google Dorking Tool: GUI for Google Custom Search API dorking with encryption, auto/manual building, and export features.",
    author="Sahir Parvez",
    author_email="parvezsahir@gmail.com",
    py_modules=["GoogleDorkingTool"],
    install_requires=[
        "requests",
        "cryptography",
        "PyQt5"
    ],
    entry_points={
        "gui_scripts": [
            "google-dorking-tool=GoogleDorkingTool:main"
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
