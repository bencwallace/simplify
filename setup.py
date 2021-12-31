from setuptools import setup, find_packages

# hacky solution for editable installs while awaiting next poetry release
setup(
    name="simplify",
    author="Ben Wallace",
    author_email="bencwallace@gmail.com",
    packages=find_packages("simplify"),
)
