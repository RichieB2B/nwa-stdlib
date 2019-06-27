from setuptools import setup

setup(
    name="nwa-stdlib",
    version="1.0.0",
    packages=["nwastdlib"],
    url="https://gitlab.surfnet.nl/automation/nwa-stdlib",
    classifiers=["License :: OSI Approved :: MIT License", "Programming Language :: Python :: 3.x"],
    license="MIT",
    author="Automation",
    author_email="automation-nw@surfnet.nl",
    description="NWA standard library.",
    install_requires=[
        "flask==1.0.3",
        "requests==2.22.0",
        "redis==3.2.1",
        "hiredis==1.0.0",
        "pytz==2019.1",
        "ruamel.yaml==0.15.97",
        "structlog==19.1.0",
    ],
    tests_require=[
        "pytest",
        "flake8",
        "black",
        "isort",
        "flake8-bandit",
        "flake8-bugbear",
        "flake8-comprehensions",
        "flake8-docstrings",
        "flake8-logging-format",
        "flake8-pep3101",
        "flake8-print",
        "mypy",
        "mypy_extensions",
        "fakeredis",
    ],
)
