from setuptools import setup, find_packages

setup(
    name="emproto",
    version="1.1",
    author="Alfisene Keita",
    description="Bezpečný přenos zpráv a souborů přes šifrování",
    url="https://github.com/certikpolik30/emproto",
    packages=find_packages(),
    install_requires=[
        "cryptography"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
