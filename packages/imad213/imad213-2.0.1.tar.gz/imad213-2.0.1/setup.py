from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="imad213",
    version="2.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "imad213 = imad213.imad:main",
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",  # هذا يحدد التنسيق
)
