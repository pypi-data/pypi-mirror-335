from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="myuiautomator",
    version="0.1",
    description="A simple library for Android UI automation using UIAutomator and ADB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodeMaster",
    author_email="theloveme400@gmail.com",
    url="https://pypi.org/project/myuiautomator/",  # ضع رابط المشروع إذا كان متاحًا
    packages=find_packages(),
    install_requires=["uiautomator"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

