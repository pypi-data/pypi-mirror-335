from setuptools import setup, find_packages

setup(
    name="bg_remover11",
    version="0.3",
    packages=find_packages(),
    install_requires=["rembg", "Pillow"],
    include_package_data=True,
)
