# setup.py
from setuptools import setup, find_packages

setup(
    name="facebook_auth",
    version="0.1.0",
    description="Un package Python per l'autenticazione con Facebook",
    author="Il Tuo Nome",
    author_email="tua@email.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
