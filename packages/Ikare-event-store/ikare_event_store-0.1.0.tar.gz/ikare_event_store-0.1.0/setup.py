"""
Configuration du package IKAREEventStore
"""

from setuptools import setup, find_packages

setup(
    name="Ikare_event_store",
    version="0.1.0",
    packages=find_packages(),
    description="Un package pour stocker et récupérer des événements associés à des dates",
    author="FETNI Mohamed",
    author_email="MFE.FETNI.MOHAMED@GMAIL.COM",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)