from setuptools import setup, find_packages

setup(
    name="shared_models_stocksblitz",
    version="0.1.1",
    packages=find_packages(),
    install_requires=["sqlalchemy", "psycopg2"],  # Add any dependencies
)