from setuptools import find_packages, setup

setup(
    name="alkin-codeguard",
    version="0.1",
    packages=find_packages(),  # Finds 'codeguard'
    install_requires=["click", "requests", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "codeguard=codeguard.cli:main",  # Points to cli.py's main()
        ],
    },
)
