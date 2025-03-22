import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sns-appointment",
    version="0.2.0",
    author="Jeena",
    author_email="jeena7758@gmail.com",
    description="A library for sending AWS SNS notifications for doctor appointments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeena7758",
    packages=setuptools.find_packages(),
    install_requires=[
        'boto3>=1.17.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)