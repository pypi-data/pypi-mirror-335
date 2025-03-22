from setuptools import setup, find_packages

setup(
    name="vascent_hello",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hello=say_hello:main',
        ],
    },
    author="vascent",
    author_email="binyang617@gmail.com",
    description="A simple command-line tool to say hello",
    keywords="hello, cli",
    python_requires=">=3.6",
) 