from setuptools import setup

setup(
    name="morethemes",
    version="0.3.1",
    packages=["morethemes"],
    description="More themes for matplotlib",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Joseph Barbier",
    author_email="joseph.barbierdarnal@gmail.com",
    url="https://github.com/JosephBARBIERDARNAL/morethemes",
    install_requires=["matplotlib"],
    include_package_data=True,
    package_data={
        "morethemes": ["fonts/*.ttf"],
    },
)
