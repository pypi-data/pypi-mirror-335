from setuptools import setup, find_packages

setup(
    name="vascent_hello",
    version="0.1.3",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'say-hello=say_hello.cli:main',
        ],
    },
    python_requires='>=3.6',
    description="A simple CLI tool that says hello",
    author="User",
    author_email="user@example.com",
) 