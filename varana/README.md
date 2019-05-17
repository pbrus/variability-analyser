# Varana
[![Build Status](https://travis-ci.org/pbrus/variability-analyser.svg?branch=master)](https://travis-ci.org/pbrus/variability-analyser)
[![Code](https://img.shields.io/badge/code-Python-blue.svg "Python")](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg "MIT license")](https://github.com/pbrus/variability-analyser/varana/blob/master/LICENSE)

This module determines the variability of stars through analyzing their time series.

![varana](http://www.astro.uni.wroc.pl/ludzie/brus/img/github/varana.gif)

## Installation

To install the package please type from the command line:
```bash
$ sudo pip3 install varana
```

## Usage

This module is the part of a larger tool - [variability-analyser](https://github.com/pbrus/variability-analyser). Despite of that it can be used separately. The module is divided into smaller scripts which can be called independently. You can use the following scripts:

+ `detrend.py`
+ `trim.py`
+ `freq_comb.py`
+ `fit.py`
+ `phase.py`
+ `plt_pdgrm.py`

To see what they do please call them with the `-h` option, for example:
```bash
$ detrend.py -h
```

## License

The **varana** module is licensed under the [MIT license](http://opensource.org/licenses/MIT).
