from setuptools import setup, find_packages

setup(
    name = "flowing",
    version = "0.0.1",
    packages=find_packages(),
    install_requires = [],
    entry_points={
        "console_scripts":[
            "flow = flowing.main:main" 
        ]
    },
    license =[ ],
)