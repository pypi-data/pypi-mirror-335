from setuptools import setup, find_packages

setup(name='rajsiri',
    version='0.1.1',
    author='Rajesh Kamireddy Author',
    author_email='rajesh17mca@gmail.com',
    description='Learning Module',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "rajesh-get = rajsiri:get_raj"
        ]
    }
)