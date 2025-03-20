from setuptools import setup, find_packages
from gpus import __version__

setup(
    name="gpus",
    version=__version__,
    description="A web interface for monitoring NVIDIA GPUs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="mrfakename",
    author_email="me@mrfake.name",
    url="https://github.com/fakerybakery/gpus",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "nvidia-ml-py",
        "click",
        "flask",
        "flask-socketio",
        "eventlet>=0.30.0",  # For WebSocket support
        "python-engineio>=4.0.0",
        "python-socketio>=5.0.0",
        "psutil",  # For process management
        "rich>=10.0.0",  # For interactive CLI
        "requests>=2.25.0",  # For API communication
    ],
    entry_points={
        "console_scripts": [
            "gpus=gpus.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "gpus": [
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
