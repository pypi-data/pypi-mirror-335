from setuptools import setup, find_packages

setup(
    name='pymlem',  # Replace with your package's name
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List dependencies here, e.g., 'numpy', 'pandas', etc.
    ],
    description='A brief description of your package',
    author='witchietherichie',
    author_email='witchietherichie@hotmal.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Adjust the license type
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify the Python version your package supports
)
