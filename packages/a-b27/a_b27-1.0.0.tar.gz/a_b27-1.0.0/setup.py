from setuptools import setup, find_packages

setup(
    name="a-b27",
    version="1.0.0",
    author="IMAD-213",
    author_email="madmadimado59@gmail.com",
    description=" Free Fire Page Hack",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/a-b27",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0.0",
        "pyngrok>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "a-b27=a_b27.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
