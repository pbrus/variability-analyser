RED='\033[0;31m'
GREEN='\033[0;32m'
BROWN='\033[0;33m'
RESET='\033[0m'


function print_welcome()
{
    echo -e ""
    echo -e " ${BROWN}Variability analyzer _||__|__${RESET}"
    echo -e ""
    echo -e " Usage: var_analyser.sh <lightcurve>"
    echo -e ""
    echo -e " Version: 0.0.0"
    echo -e " Przemysław Bruś"
    echo -e ""
}

function print_tasks()
{
    echo -e ""
    echo -e "What do you want to do with the lightcurve?"
    echo -e " ${RED}c${RESET} - calculate the Fourier Transform"
    echo -e " ${RED}e${RESET} - edit the frequencies table and fit a model"
    echo -e " ${RED}p${RESET} - phase the lightcurve"
    echo -e " ${RED}d${RESET} - detrend the residuals"
    echo -e " ${RED}t${RESET} - trim the residuals"
    echo -e " ${RED}r${RESET} - restart the analysis"
    echo -e " ${RED}q${RESET} - quit a program"
    echo -e ""
}

function print_sines_parameters()
{
    echo -e ""
    echo -e " ${GREEN}  amplitude       frequency          phase_angle${RESET}"
}

function print_model_yintercept()
{
    echo -e " ${GREEN}  y_intercept${RESET}"
}

function print_choose_frequency()
{
    echo -e " ${RED}Choose the frequency from the table:${RESET}"
}

function print_hashbar()
{
    echo -e " ${GREEN}---------------${RESET}"
}
