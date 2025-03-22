from setuptools import setup, find_packages

setup(
    name="bg_remover_lk",
    version="1.0",
    packages=find_packages(),
    install_requires=["rembg", "Pillow"],
    include_package_data=True,
)
