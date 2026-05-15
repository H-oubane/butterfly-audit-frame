# setup.py
from setuptools import setup, find_packages

setup(
    name="risk-scorer",
    version="1.0.0",
    description="Device Integrity Risk Scorer — Audit défensif Android",
    packages=find_packages(),
    py_modules=["audit"],
    install_requires=[
        "frida",
        "frida-tools",
        "drozer",
    ],
    entry_points={
        "console_scripts": [
            "risk-scorer=audit:main",
        ],
    },
    python_requires=">=3.9",
)