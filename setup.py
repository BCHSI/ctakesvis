
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conceptvis", # Replace with your own username
    packages=['conceptvis',],
    version="0.0.1",
    author="Dima Lituiev",
    author_email="d.lituiev@gmail.com",
    description="package for concept (rich named entity) visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pandas'],
    package_data = {'conceptvis':
                    ['static/*.css', 'static/*.js', 'static/tabulator/dist/js/tabulator.min.js']
                    },
    #packages=setuptools.find_packages(),
    # url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

