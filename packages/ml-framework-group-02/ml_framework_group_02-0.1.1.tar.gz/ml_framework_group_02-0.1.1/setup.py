from setuptools import setup

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ml_framework_group_02',  # Updated name to ensure uniqueness
    version='0.1.1',    
    description='A concise machine learning framework for educational purposes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='BSD 2-clause',
    packages=['ml_framework_group_02'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'plotly',
        'tqdm',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
