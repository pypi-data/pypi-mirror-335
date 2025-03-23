from setuptools import setup, find_packages

setup(
    name='alpaca-transformer',  # The name of your package
    version='0.1.8.4',  # Version number
    packages=find_packages(),  # This will automatically find all packages in your project
    install_requires=[  # Dependencies that will be installed with your package
        'torch>=2.6.0',  # Add your dependencies here
    ],
    description='Alpaca - a custom transformer model implementation',
    long_description=open('README.md').read(),  # Read the README file for the long description
    long_description_content_type='text/markdown',  # Mark it as a markdown README
    author='RazielMoesch',
    author_email='razielsoccer@gmail.com',
    url='https://github.com/RazielMoesch/alpaca',  # Link to your project's repo
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Corrected to MIT License
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Set the minimum Python version requirement
    #license='MIT',  # Changed to MIT License
)
