from setuptools import find_packages, setup

with open("README.md") as f:
    long_descr = f.read()
    
with open("python_fib/version") as f:
    version = f.read()

setup(
    name="python_fib_study",
    version=version,
    author="neznakomec16",
    description="Calculates a Fibonacci number",
    long_description=long_descr,
    url="https://github.com/Neznakomec16/python-fib",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "PyYAML>=4.1.2",
        "dill>=0.2.8",
    ],
    extras_require={
        "server": ["Flask>=1.0.0"],
    },
    python_requires=">=3",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "fib_number=python_fib.cmd.fib_numb:fib_numb",
        ]
    },
    license="MIT",
)