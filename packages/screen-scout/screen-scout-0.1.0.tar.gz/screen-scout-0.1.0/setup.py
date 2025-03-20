from setuptools import setup, find_packages

setup(
    name="screen-scout",
    version="0.1.0",
    description="Automated UI testing tool",
    author="Your Name",
    author_email="jamesleyJoseph@email.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "nest_asyncio"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "screen-scout = main:main"
        ]
    },
)
