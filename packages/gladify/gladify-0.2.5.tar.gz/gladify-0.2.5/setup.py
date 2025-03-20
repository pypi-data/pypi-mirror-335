from setuptools import setup, find_packages

setup(
    name="gladify",
    version="0.2.5",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "gladify.GladUI": ["GladUI.png"],  # Ensures the default icon is included
    },
    install_requires=[
        "pygame",
        "pillow",
    ],
    author="Navthej",
    author_email="gladgamingstudio@gmail.com",
    description="A Python package for various utilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    zip_safe=False,  # Ensures files are extracted
)
