from setuptools import setup, find_packages

setup(
    name="donware",
    version="0.2.0",
    author="Don Yin",
    author_email="Don_Yin@outlook.com",
    description="Don's personal toolkits for data science and machine learning.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Don-Yin/donware",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
