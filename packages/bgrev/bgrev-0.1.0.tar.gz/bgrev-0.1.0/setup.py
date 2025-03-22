from setuptools import setup, find_packages

setup(
    name='bgrev',
    version='0.1.0',
    description='A simple package to remove image backgrounds using rembg.',
    author='Harshith Chandra',
    author_email='your_email@example.com',  # <-- You can update this
    packages=find_packages(),
    install_requires=[
        'rembg',
        'Pillow'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
