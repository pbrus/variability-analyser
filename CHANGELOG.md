# Variability Analyser Changelog
## [1.0.0] 2020-11-25
### Added
* Mechanism checking whether a new found frequency can cause that the model does not converge
* Parameters to `var.config`:
  * `LC_NODES_NUMBER`
  * `FT_STEP`
  * `FREQ_LINCOMB_MIN_COEFF`
  * `FREQ_LINCOMB_MAX_COEFF`
  * `FREQ_LINCOMB_MAX_HARM`
* Mechanism to remember the last number of nodes used to detrend the data/residuals
* `Dockerfile` to run tests locally

### Changed
* **[Algorithm] to compute a linear combination of frequencies** :exclamation:
* Update `varana` package to version `1.0.0`:
  * **Break compatibility with Python 3.5** :exclamation:
  * Migrate to Python >= 3.6
  * Update the algorithm to compute a linear combination of frequencies by `freq_comb.py`
  * Add `max_harm` parameter to `freq_comb.py` and `fit.py` scripts
  * Remove `filterwarnings` ignoring the fact that the model can not converge to the data
  * Increase float precision of residuals and after trimming the data from `.4f` to `.7f`
  * Refactor code: add type hints, reformat code using [Black]
  * Change default values in scripts
* Installation script:
  * Root privileges only needed to install the `varana` package
  * Store a reference to **variability-analyser** in `.bash_profile` instead `.bashrc`
* Documentation

### Fixed
* Restart (not overwrite) the residuals file each time when the number of nodes is updated interactively

### Removed
* Parameters from `var.config`:
  * `FT_STEP_FACTOR`
  * `FREQ_LINCOMB_FACTOR`

## [0.1.0] 2019-05-18
### Added
* Initial version

[Algorithm]: doc/usage.md#frequencies
[Black]: https://github.com/psf/black
