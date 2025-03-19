#Courtesy of https://www.freecodecamp.org/news/build-your-first-python-package/
from setuptools import setup, find_packages

VERSION = '0.1' 
DESCRIPTION = 'Markov Chain Monte Carlo curve fitting'
LONG_DESCRIPTION = 'Metropolis-Hastings MCMC algorithm, along with helper functions for curve fitting and visualization'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="Squires-McFit", 
        version=VERSION,
        author="Andrés Cook",
        author_email="<andcook5@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=["numpy", "matplotlib.pyplot", "corner", "typing", "progress.bar"], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'

        keywords=['python', 'fitting'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)