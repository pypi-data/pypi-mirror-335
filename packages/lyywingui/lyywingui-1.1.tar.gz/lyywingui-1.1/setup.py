from setuptools import setup

setup(
    name='lyywingui',
    version='1.1',
    author='lyy',
    author_email='',
    description='lyywingui for lyy',
    #packages=find_packages(),
    license="MIT",
    install_requires=[
        'psutil>=5.9.0',  
        'pywin32>=300',  
        'fuzzywuzzy>=0.18.0',  
        'python-Levenshtein>=0.12.0' 
    ],
)