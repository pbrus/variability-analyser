function welcome_message()
{
    print_welcome
    exit 1
}

function display_tasks()
{
    print_tasks
    local answer

    while read answer
    do
        for option in c e p d t r q
        do
            if [ "$answer" == "$option" ]
            then
                display_specific_task $option
                break 2
            fi
        done

        print_tasks
    done
}

function display_specific_task()
{
    local option=$1

    case $option in
    c)
        calculate_fourier_transform
        display_tasks
        ;;
    e)
        edit_frequencies_table
        display_tasks
        ;;
    p)
        phase_lightcurve
        display_tasks
        ;;
    d)
        detrend_residuals
        display_tasks
        ;;
    t)
        trim_residuals
        display_tasks
        ;;
    r)
        restart_analysis
        display_tasks
        ;;
    q)
        exit
        ;;
    esac
}

function calculate_fourier_transform()
{
    if [ -e ${RESID_FILE} ]
    then
        fourier_transform ${RESID_FILE}
    else
        fourier_transform ${lightcurve_filename}
    fi
}

function fourier_transform()
{
    local step=`awk '{if (NR==1) t0=$1} END {
                printf("%f\n", '${FT_STEP_FACTOR}'/($1-t0))}' $1`

    fnpeaks -f $1 ${FT_START} ${FT_STOP} ${step} > /dev/null

    local fourier_transform_file=`basename -s ${LC_SUFFIX} $1`".trf"
    local fourier_transform_max_file=`basename -s ${LC_SUFFIX} $1`".max"

    grep -v "%" ${fourier_transform_max_file}
    plt_pdgrm.py ${fourier_transform_file} --display
}

function edit_frequencies_table()
{
    ${EDITOR} frequencies_table
    fit.py ${lightcurve_filename} --freq `cat frequencies_table` \
    --resid ${RESID_FILE} > ${MODEL_FILE}

    display_current_model
}

function display_current_model()
{
    print_sines_parameters
    awk 'NR > 1 {print $0}' ${MODEL_FILE}
    print_model_yintercept
    awk 'NR == 1 {print $0}' ${MODEL_FILE}
}

function phase_lightcurve()
{
    local frequency

    print_choose_frequency
    cat frequencies_table
    print_hashbar
    read frequency

    phase.py ${lightcurve_filename} ${frequency} --model ${MODEL_FILE} --display
}

function detrend_residuals()
{
    detrend_data ${RESID_FILE}
    remove_files_or_dirs ${RESID_FILE/${LC_SUFFIX}/.png}
}

function trim_residuals()
{
    trim.py ${RESID_FILE} ${RESID_FILE} --display
}

function restart_analysis()
{
    local fourier_transform_file=`basename -s ${LC_SUFFIX} \
                                  ${lightcurve_filename}`".trf"
    local fourier_transform_max_file=`basename -s ${LC_SUFFIX} \
                                  ${lightcurve_filename}`".max"

    remove_files_or_dirs ${fourier_transform_file} \
                         ${fourier_transform_max_file} model${LC_SUFFIX} \
                         resid${LC_SUFFIX} resid.trf resid.max frequencies_table
}
