from setuptools import find_packages, setup

with open("README.md") as f:
    long_descr = f.read()

setup(
    name="python_fib_study",
    version="0.0.1",
    author="neznakomec16",
    description="Calculates a Fibonacci number",
    long_description=long_descr,
    url="https://github.com/Neznakomec16/python-fib",
    packages=find_packages(exclude=("tests",)),
    install_requires=[],
    python_requires=">=3",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "fib_number=python_fib.cmd.fib_numb:fib_numb",
        ]
    },
)
