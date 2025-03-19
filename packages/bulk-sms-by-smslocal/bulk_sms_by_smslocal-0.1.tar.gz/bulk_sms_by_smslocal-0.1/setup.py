from setuptools import setup, find_packages

setup(
    name="bulk_sms_by_smslocal",  # Replace with your package name
    version="0.1",
    author="Ariyan Khan",
    author_email="ariyan@mycountrymobile.com",
    description="A Python package to send bulk SMS using an external API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Smslocal001/bulk-sms",  # Replace with your GitHub URL
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
