# Usage

To see how to use **variability-analyser** properly we perform an analysis of a synthetic data. At the beginning check [how to prepare](configuration.md) a `config` file. In this tutorial we use a default `config` file which is attached to the repostiory and is ready to use after installation. To demonstrate consecutive steps we use a synthetic time series of RR Lyrae variable.

## Data preparation

Let's prepare the data firstly. We call the main script to remove a trend:
```bash
var_analyser.sh lightcurves/rr_lyr_lc.dat
```
We get an image of the time series and a spline with 9 (default) nodes marked by red dots:

<img src="resources/rr_lyr_detrend-1.png" width="800" alt="rr_lyr_detrend-1.png">

A spline describes the trend between observational seasons. The script asks us:
```
Is OK? [y/n]:
```
We can change the number of nodes. If we type `n` then `11`, we get the following fitting:

<img src="resources/rr_lyr_detrend-2.png" width="800" alt="rr_lyr_detrend-2.png">

It seems to be right. In the next step the software removes the trend and performs sigma clipping on the time series automatically. After that an interactive window appears. If the result is not satisfactory, we can improve it just clicking on the window twice. All points lying outside two horizontal lines are removed and colored by red:

<img src="resources/rr_lyr_trim.png" width="800" alt="rr_lyr_trim.png">

According to the `config` file two new directories are created in the current directory:

+ `lightcurves_detrend/`
+ `lightcurves_trim/`

The directories store text files of a modified time series and PNG images of final data preparation.

> :point_right: **_NOTE:_** If we break the program's flow at this moment, the next call of `var_analyser.sh` will reuse these files.

## Variability analysis

Now we are ready to start the main analysis. In the next step we can see the following menu:
```
What do you want to do with the light curve?
 c - calculate the Fourier Transform
 e - edit the frequencies table and fit a model
 p - phase the light curve
 d - detrend the residuals
 t - trim the residuals
 f - change fourier parameters
 r - restart the analysis
 s - save the results
 q - quit the program
```
The menu is always printed after each operation. At the beginning we choose `c` option to calculate the Fourier Transform. After a while we can see a listing which contains ten most significant frequencies in a periodogram:
```
    0     1.214720     0.823235    0.15958    60.88
    1     1.217476     0.821371    0.09308    35.51
    2     1.211990     0.825089    0.09055    34.54
    3     2.429466     0.411613    0.07942    30.30
    4     2.432196     0.411151    0.04482    17.10
    5     3.644186     0.274410    0.04432    16.91
    6     2.426736     0.412076    0.04402    16.80
    7     1.215084     0.822988    0.03539    13.50
    8     1.214382     0.823464    0.03487    13.30
    9     1.206504     0.828841    0.02889    11.02
```
The columns represent from left to right:
+ index
+ frequency (cycle/day)
+ period (day)
+ amplitude (magnitudo)
+ singal to noise ratio - S/N

Moreover, we can inspect the whole periodogram on the image:

<img src="resources/rr_lyr_periodogram-1.png" width="800" alt="rr_lyr_periodogram-1.png">

Now we should choose `e` option to save a frequency with the highest amplitude to the frequencies table. In our case it will be `1.214720`.

> :point_right: **_NOTE:_** The frequencies table is a text file. This file will be opened using an editor pointed by `EDITOR` variable. See [configuration.md](configuration.md).

The software will fit a single sine to the time series using a non-linear least squares method. The model is printed on the screen:
```
amplitude       frequency        phase_angle
0.1585247297    1.2147303440     2.5101232542
y_intercept
17.3748020604
```
In the background the software calculates residuals subtracting the model from the time series. In the next steps we'll work on residuals instead of an original time series. We can correct residuals detrending or trimming them in the same way as we did in the data preparation section (option `d` or `t`).

We should find another significant frequencies. Hence we repeat `c` and `e` options. Four consecutive values saved to the table frequencies look like:
```
1.214720
2.429466
3.644186
4.858932
```
The final model is composed of sum of four sines with the following parameters:
```
amplitude       frequency        phase_angle
0.1589109516    1.2147298878     2.5178341388
0.0793181721    2.4294597755     1.9146753253
0.0457743639    3.6441896633     1.5754808929
0.0164677927    4.8589195511     1.1005553983
y_intercept
17.3740450844
```
To check the model we can display it on a phased light curve. To do this we choose `p` option and then select the most significant frequency with the highest amplitude: `1.2147298878`:

<img src="resources/rr_lyr_phase.png" width="800" alt="rr_lyr_phase.png">

> :point_right: **_NOTE:_** If there are very small amplitudes of sines a model may not fit to a phased light curve accurately. It doesn't imply that the model is improper at all.

At the end we save results selecting `s` option. If a star is variable we answer `y`, phase the light curve and add some comment about the star, for example:
> RR Lyrae star

All results will be stored in a directory pointed by `RESULTS_DIR` including a log file with comments for many time series.
