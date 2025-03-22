from setuptools import setup, find_packages


def get_version():
    with open("sbi_special_docx_master/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    raise RuntimeError("Unable to find version string.")


setup(
    name="sbi_special_docx_master",
    version=get_version(),
    packages=find_packages(),
    package_data={},
    install_requires=[
        'python-docx~=1.1.2',
        'pydantic~=2.0',
        'pillow~=11.1.0',
        'pytest~=8.3.5'
    ],
    extras_require={
        'dev_deps ': [
            'pytest',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    description="A project for adding an information block to an MS .docx file",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Danila Aleksandrov",
    author_email="danila.alexandrov24@gmail.com",
    python_requires='>=3.10',
)
