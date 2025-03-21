from setuptools import setup, find_packages

setup(
    name="DisNet",
    version="0.1",
    packages=find_packages(),
    install_requires=["discord", "dotenv"],  # Здесь зависимости, если нужны
)
