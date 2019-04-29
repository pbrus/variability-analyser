import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="varana",
    version=__import__("varana").__version__,
    author="Przemysław Bruś",
    description="Analyse the variability of stars",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbrus/variability-analyser/varana",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=["numpy", "scipy", "matplotlib", "scikit-learn"],
    scripts=[
        "scripts/detrend.py",
        "varana/trim.py",
        "scripts/freq_comb.py",
        "scripts/fit.py",
        "scripts/phase.py",
        "scripts/plt_pdgrm.py",
    ],
    tests_require=["pytest"],
    keywords=["variability", "time", "series", "stars", "magnitude"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Utilities",
    ],
)
