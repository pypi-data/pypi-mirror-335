from setuptools import setup, find_packages

setup(
    name='corerec',
    version='0.4.1.1',
    description='A Framework to built custom recommendors.',
    author='Vishesh Yadav',
    author_email='vishesh@corerec.tech',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'networkx',
        'scikit_learn',
        'cr_learn',
        'torch',
        'tqdm',
        'memory_profiler',
        'pandas',
        'torch_geometric',
        'dask',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)