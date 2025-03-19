from setuptools import setup, find_packages

setup(
    name="emproto",
    version="0.7.0",
    author="Alfisene Keita",
    description="Bezpečný přenos zpráv a souborů přes šifrování",
    url="https://github.com/certikpolik3/EM-Proto",
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
