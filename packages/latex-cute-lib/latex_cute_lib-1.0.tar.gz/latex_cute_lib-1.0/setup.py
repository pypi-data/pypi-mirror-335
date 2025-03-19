from setuptools import setup, find_packages
"""
building cmd command: python setup.py sdist
python setup.py sdist bdist_wheel
uploading command: twine upload dist/*
"""
setup(
    name='latex-cute-lib',
    version='1.0',
    packages=find_packages(),
    author='Grigoreva Darya'
)

