from setuptools import setup, find_packages

setup(
    name="RedXAIEasyFunctions",
    version="0.1.0",
    description="A Python toolkit to simplify and enhance basic functions.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="MainDirectory",
    author_email="RedXDevelopment1998@gmail.com",  # ✅ This is valid
    url="https://github.com/YourUsername/RedXAIEasyFunctions",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
