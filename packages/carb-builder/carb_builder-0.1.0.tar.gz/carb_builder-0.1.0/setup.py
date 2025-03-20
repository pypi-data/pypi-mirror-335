from setuptools import setup, find_packages

setup(
    name='carb_builder', 
    version='0.1.0',
    description='A Python package for building and simulating carbohydrate structures.',
    author='Ayodele Faleti',
    author_email='ayodele.ayodele@gmail.com',  
    packages=find_packages(),
    install_requires=[
        'openmm',
        'numpy'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)