# Variability-analyser
[![Build Status](https://travis-ci.org/pbrus/variability-analyser.svg?branch=master)](https://travis-ci.org/pbrus/variability-analyser)
[![Code](https://img.shields.io/badge/code-Python-blue.svg "Python")](https://www.python.org/)
[![Code](https://img.shields.io/badge/code-Bash-green.svg "Bash")](https://www.gnu.org/software/bash/)
[![GitHub release](https://img.shields.io/badge/ver.-0.1.0-brightgreen.svg "download")](https://github.com/pbrus/variability-analyser)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg "MIT license")](https://github.com/pbrus/variability-analyser/blob/master/LICENSE)

This package allows to analyze the variability of stars and determine shapes of their light curves.

<img src="http://www.astro.uni.wroc.pl/ludzie/brus/img/github/variability.svg" width="800" alt="variability-analyser">

## Introduction

The package is composed of three parts:
+ [*FNPEAKS*](http://helas.astro.uni.wroc.pl/deliverables.php?active=fnpeaks&lang=en) for efficient calculation of Fourier amplitude spectra
+ Python module [*varana*](https://pypi.org/project/varana/) for analyzing time series
+ Bash wrapper as a user-friendly text interface

## Installation

To install the package please type from the command line:
```bash
$ git clone https://github.com/pbrus/variability-analyser
$ cd variability-analyser
$ bash install
```
Set the `installation directory`, download and install essential components automatically.

#### Uninstallation

To uninstall the software entirely remove the `installation directory`.

## Usage

To get more info please check the [doc](doc) directory.

## Contribution

New feature, bugs? Issues and pull requests are welcome.

## License

**Variability-analyser** is licensed under the [MIT license](http://opensource.org/licenses/MIT). Note that [*FNPEAKS*](http://helas.astro.uni.wroc.pl/deliverables.php?active=fnpeaks&lang=en) is a third-party software component.
