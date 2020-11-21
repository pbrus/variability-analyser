# Configuration

To work with **variability-analyser** properly we need a `config` file. The `config` file is a text file which contains a set of variables. These variables are divided into sections and are described below.

## Content
#### [ Lightcurves ]

This section contains variables which mainly describe text files containing light curves.

| variable name   | meaning                                               |
| --------------- | ----------------------------------------------------- |
| LC_DIR          | directory to store light curves                       |
| LC_DETERND_DIR  | directory to store detrended light curves             |
| LC_TRIM_DIR     | directory to store detrended and trimmed light curves |
| LC_TIME_COLUMN  | column to store time                                  |
| LC_MAG_COLUMN   | column to store magnitude                             |
| LC_ERR_COLUMN   | column to store error of magnitude                    |
| LC_NODES_NUMBER | initial number of nodes to detrend light curves       |
| LC_TIME_PREFIX  | value which will be subtracted from time column       |
| LC_SUFFIX       | extension of light curves files                       |

If directories don't exist, they will be created automatically.

#### [ Fourier Transform ]

In this section you can set parameters of Fourier Transform (FT).

| variable name | meaning                                                             |
| ------------- | ------------------------------------------------------------------- |
| FT_START      | the beginning of the range for which the FT is computed (cycle/day) |
| FT_STOP       | the end of the range for which the FT is computed (cycle/day)       |
| FT_STEP       | interval for which the FT is computed (cycle/day)                   |
| RESID_FILE    | temporary file for residuals                                        |
| MODEL_FILE    | temporary file for model                                            |

#### [ Frequencies combination ]

| variable name          | meaning                                                                  |
| ---------------------- | ------------------------------------------------------------------------ |
| FREQ_LINCOMB_MIN_COEFF | Minimal value for each coefficient of linear combinations of frequencies |
| FREQ_LINCOMB_MAX_COEFF | Maximal value for each coefficient of linear combinations of frequencies |
| FREQ_LINCOMB_MAX_HARM  | Maximal value for each harmonic of linear combinations of frequencies    |

Let's assume that we want to calculate linear combination of three frequencies `f1`, `f2`, `f3` and:

* FREQ_LINCOMB_MIN_COEFF = -3
* FREQ_LINCOMB_MAX_COEFF = 3
* FREQ_LINCOMB_MAX_HARM = 5

The program will generate all combinations from -3 to 3:
```python
f = -3*f1 - 3*f2 - 3*f3
f = -2*f1 - 3*f2 - 3*f3
...
f = 0*f1 + 2*f2 + 0*f3  # harmonic of f2
...
f = 3*f1 + 3*f2 + 2*f3
f = 3*f1 + 3*f2 + 3*f3
```
and all harmonics (which are more likely than complex combinations):
```python
f = 4*f1
f = 4*f2
...
f = 5*f2
f = 5*f3
```
Splitting into two groups is necessary due to the fact that for many frequencies computing of all combinations is time consuming.

#### [ Other ]

| variable name       | meaning                                  |
| ------------------- | ---------------------------------------- |
| EDITOR              | your favourite text editor               |
| RESULTS_DIR         | directory to store results               |
| RESULTS_LOG         | log file to store comments about objects |

## Location

There are two possible ways to work with the `config` file. The default file is named as `var.config` and is located in your `installation directory`. You can edit it to have a global configuration file. If you call the main script without `--config` option:
```
$ var_analyser.sh <path/to/lightcurve>
```
the script will parse the global configuration file. The alternative way is to use `--config` option which points the path to another `config` file:
```
$ var_analyser.sh <path/to/lightcurve> --config <path/to/config_file>
```
> :bulb: **_HINT:_**  If your local `config` file has the same name as the global one, i.e. `var.config` and is located in the current directory, i.e. `./`, please use the following call:
> ```
> $ var_analyser.sh <path/to/lightcurve> --config ./var.config
> ```
> to overwrite global configuration. `--config var.config` doesn't overwrite a content of the global `config`.
