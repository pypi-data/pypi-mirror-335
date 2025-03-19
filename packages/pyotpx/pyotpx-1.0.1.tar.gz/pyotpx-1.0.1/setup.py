from setuptools import setup, find_packages

setup(
    name="pyotpx",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[],
    author="NotHerXenon",
    author_email="PyOTPX@gmail.com",
    description="A free and secure OTP system with email verification",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
