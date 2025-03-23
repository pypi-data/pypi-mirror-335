from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

with open("gen_api/_version.py") as version_file:
    for line in version_file:
        if "__version__" in line:
            __version__ = line.split()[-1].replace('"', "")

setup(
    name="gen10",
    version="1.3",
    author="Joan Alcaide-Núñez",
    author_email="joanalnu@outlook.com",
    description="API to use the functions of the Genetics10 project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/joanalnu/gen_api',
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix'
    ],
    package_data={"gen_api": ["static/*"]},
    include_package_data=True,
)