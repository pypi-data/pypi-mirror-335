from setuptools import setup

installation_requirements = [
    "openai==1.66.3",
    "loguru==0.7.3",
    "neo4j==5.28.1"
]

setup(
    version="0.2",
    name="freeflock-contraptions",
    description="A collection of contraptions",
    author="(~)",
    url="https://github.com/freeflock/contraptions",
    package_dir={"": "packages"},
    packages=["freeflock_contraptions"],
    install_requires=installation_requirements,
)
