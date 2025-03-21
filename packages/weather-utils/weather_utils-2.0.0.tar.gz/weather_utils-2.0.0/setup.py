import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="weather_utils",
    version="2.0.0",
    author="Srihari Kata",
    author_email="x24155331@student.ncirl.ie",  
    description="A utility package for weather data handling with AWS services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sriharikata/Weather-Utils/tree/main/weather_utils", 
    packages=["weather_utils"],
    install_requires=["requests","boto3","python-dotenv"],  # Required dependencies
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

