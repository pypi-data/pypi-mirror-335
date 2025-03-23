from setuptools import setup, find_packages

setup(
    name='py_volanalytics',
    version='0.1.0',
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    install_requires=[
        'aleatory>=1.0.1',
        'attrs>=25.3.0',
        'ipykernel>=6.29.5',
        'ipython>=9.0.2',
        'numpy>=2.2.4',
        'latex>=0.7.0',
        'matplotlib>=3.10.1',
        'scienceplots>=2.1.1',
        'setuptools>=77.0.3',
    ],
    extras_require={
        "dev":["pytest>=7.0", 'twine>=6.1.0',]
    },
    author="quasar-chunawala",
    author_email="quasar.chunawala@gmail.com",
    license="MIT",
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent"
    ],
    url="https://github.com/quasar-chunawala/py_volanalytics",
)