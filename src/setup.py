from setuptools import setup

setup(
    name="codesearch",
    version="0.1",
    packages=["codesearch"],
    install_requires=["pyinotify", "attr"],
    entry_points={"console_scripts": ["codesearch=codesearch.cli:main"]},
)
