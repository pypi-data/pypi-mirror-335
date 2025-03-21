from setuptools import setup, find_packages
setup(
    name='pazok',
    version='0.2.0.9',
    author='b_azo',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
        classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
