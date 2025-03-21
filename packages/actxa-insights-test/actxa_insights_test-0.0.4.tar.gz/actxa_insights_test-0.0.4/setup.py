from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="actxa_insights_test",
    version="0.0.4",
    packages=find_packages(),
    description="SDK Python package for Actxa Insights",
    author="Actxa Insights",
    author_email="hadrian.gunawan@inphosoft.com",
    # url="https://github.com/yourusername/my-package",
    python_requires=">=3.9",
    install_requires=["requests"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
