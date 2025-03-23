from setuptools import setup, find_packages

# Read the README file
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Setup function
setup(
    name='image_capturer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['opencv-python'],
    author='Asmit Jha',
    author_email='asmitjha0812@gmail.com',
    description='A simple library to capture images using a webcam.',
    long_description=long_description,  # Pass the variable, not the open statement
    long_description_content_type='text/markdown',
    url='https://github.com/asmit-jha/image_capturer',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
      python_requires='>=3.6',
)
