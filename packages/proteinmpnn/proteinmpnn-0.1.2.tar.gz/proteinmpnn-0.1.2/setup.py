from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()
    
setup(
    name="proteinmpnn",
    version="0.1.2",
    description="a slightly cleaned up installable version of ProteinMPNN",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Markusjsommer/ProteinMPNN",
    author="installable version by markus. originally and primarily authored by Justas Dauparas.",
    author_email = "installable: markusjsommer@gmail.com ; original: justas@uw.edu",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    install_requires=["torch>=2.1.2",
                      "torchvision>=0.16.2",
                      "torchaudio>=2.1.2",
                      "typing-extensions>=4.9.0",
                      "numpy>=1.24.4, <2",
                      "setuptools"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2", "pytest-cov>=4.0", "wheel"],
    },
    python_requires=">=3.9, <3.13",
    entry_points={
       'console_scripts': [
            'proteinmpnn = proteinmpnn.protein_mpnn_run:main',
            'protein_mpnn_run = proteinmpnn.protein_mpnn_run:main',
        ],
    },
    include_package_data=True,
    package_data={'': ['/data/vanilla_model_weights/*.pt',
                       '/data/soluble_model_weights/*.pt',
                       '/data/vanilla_model_weights/*.pt']},
    
)
