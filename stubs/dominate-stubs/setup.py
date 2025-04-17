from setuptools import setup

setup(
    packages=["dominate-stubs"],
    package_data={"dominate-stubs": ["src/dominate-stubs/*.pyi"]},
    package_dir={"": "src"},
)
