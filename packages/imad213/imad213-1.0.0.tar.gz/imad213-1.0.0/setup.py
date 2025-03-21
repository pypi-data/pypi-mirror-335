from setuptools import setup, find_packages

setup(
    name="imad213",
    version="1.0.0",  # تأكد من تغيير الإصدار
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4"
    ],
    entry_points={
        "console_scripts": [
            "imad213 = imad213.imad:main",
        ]
    },
)

