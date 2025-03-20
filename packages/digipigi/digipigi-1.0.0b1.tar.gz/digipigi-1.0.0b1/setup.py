from setuptools import setup

setup(
    name="digipigi",    # Package name
    version="1.0.0b1",  # Beta Version
    description="API to use the digipigi",    author="Sebastian Huber",
    author_email="huberse@phys.ethz.ch",
    url="https://gitlab.phys.ethz.ch/cmtqo-projects/delicate/digipigi.git",
    packages=[],
    py_modules=["digipigi.digipigi"], 
    entry_points={
        'console_scripts': [
            'testDP = digipigi.testDP:main',
        ],
    },
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.18.0"
    ]
)
