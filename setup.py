from setuptools import setup, find_packages

setup(
    name="castload",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "playwright==1.40.0",
        "requests==2.31.0",
        "flask==3.1.2",
        "flask-cors==6.0.1",
        "gunicorn==20.1.0"
    ],
    entry_points={
        "console_scripts": [
            "postinstall=postinstall:main",
        ],
    },
)