# python3 setup.py sdist bdist_wheel
# twine upload dist/*
# pypi-AgEIcHlwaS5vcmcCJGU1YTc5YTFlLWVlMTAtNGM0MS04M2FjLTY1ZGIwMWYzY2IwZQACKlszLCI1MjFjNTU2ZC1lNTA1LTQwYTMtYThiMS1mYjFkYjRiZGNlYzYiXQAABiCEO4iMkICcmaCy1psSv4KpoJtzQPhFyaAxhbFFDM-pkg

from setuptools import setup, find_packages

setup(
    name='train_toolkits',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        
    ],
    author='hky3535',
    author_email='hky3535@163.com',
    description='train_toolkits',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hky3535/train_toolkits',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
