from setuptools import setup, find_packages

setup(
    name='bgremv-aditx',
    version='0.2.0',
    description='A simple package to remove image backgrounds using rembg.',
    author='Aditya',
    author_email='aditxgupta@gmail.com',  # <-- You can update this
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)


