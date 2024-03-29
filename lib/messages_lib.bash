RED='\033[0;31m'
GREEN='\033[0;32m'
BROWN='\033[0;33m'
RESET='\033[0m'


function print_welcome()
{
    echo -e ""
    echo -e " ${BROWN}Variability analyser _||__|__${RESET}"
    echo -e ""
    echo -e " Usage: var_analyser.sh <path/to/lightcurve>"
    echo -e ""
    echo -e " Options:"
    echo -e "   --config /path/to/config_file"
    echo -e ""
    echo -e ""
    echo -e " Version: 1.1.0"
    echo -e " https://github.com/pbrus"
    echo -e ""
}

function print_tasks()
{
    echo -e ""
    echo -e "What do you want to do with the light curve?"
    echo -e " ${RED}c${RESET} - calculate the Fourier Transform"
    echo -e " ${RED}e${RESET} - edit the frequencies table and fit a model"
    echo -e " ${RED}p${RESET} - phase the light curve"
    echo -e " ${RED}d${RESET} - detrend the residuals"
    echo -e " ${RED}t${RESET} - trim the residuals"
    echo -e " ${RED}f${RESET} - change fourier parameters"
    echo -e " ${RED}r${RESET} - restart the analysis"
    echo -e " ${RED}s${RESET} - save the results"
    echo -e " ${RED}q${RESET} - quit the program"
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
    echo -e " ${RED}Choose the frequency:${RESET}"
}

function print_hashbar()
{
    echo -e " ${GREEN}---------------${RESET}"
}

function print_leave_value_enter()
{
    echo -e " No changes? Press ENTER"
}

function print_fourier_parameter()
{
    echo -e " ${GREEN}$1${RESET} = ${!1}"
    print_leave_value_enter
    print_hashbar
}

function print_save_results()
{
    echo -e " ${BROWN}Saving the results to the \"${RESULTS_DIR}\" directory...\
              ${RESET}\n"
}

function print_question_about_variability()
{
    echo -e " ${RED}Is the object variable?${RESET}"
    print_hashbar
}

function print_phase_lightcurve()
{
    echo -e " ${GREEN}Phase the light curve${RESET}"
}

function print_write_comment()
{
    echo -e " ${RED}Write a comment about ${lightcurve_filename} object:\
              ${RESET}"
}

function print_file_not_exists()
{
    echo -e " ${RED}File $1 doesn't exist!${RESET}"
}
