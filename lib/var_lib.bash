function welcome_message()
{
    print_welcome
    exit 0
}

function display_tasks()
{
    print_tasks
    local answer

    while read answer
    do
        for option in c e p d t f r s q
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
        phase_lightcurve "--display"
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
    f)
        change_fourier_parameters
        display_tasks
        ;;
    r)
        restart_analysis
        display_tasks
        ;;
    s)
        save_results
        clean_working_dir
        ;;
    q)
        exit 0
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
    fnpeaks -f $1 ${FT_START} ${FT_STOP} ${FT_STEP} > /dev/null

    local fourier_transform_file=`basename -s ${LC_SUFFIX} $1`".trf"
    local fourier_transform_max_file=`basename -s ${LC_SUFFIX} $1`".max"

    grep -v "%" ${fourier_transform_max_file}
    plt_pdgrm.py ${fourier_transform_file} --display
}

function edit_frequencies_table()
{
    local epsilon=`awk '{if (NR==1) t0=$1} END {
                   printf("%f\n", '${FREQ_LINCOMB_FACTOR}'/($1-t0))}' \
                   ${lightcurve_filename}`

    ${EDITOR} frequencies_table
    fit.py ${lightcurve_filename} \
        --freq `cat frequencies_table` \
        --resid ${RESID_FILE} \
        --min ${FREQ_LINCOMB_MIN_COEFF} \
        --max ${FREQ_LINCOMB_MAX_COEFF} \
        --max_harm ${FREQ_LINCOMB_MAX_HARM} \
        --eps ${epsilon} > ${MODEL_FILE}

    display_current_model
}

function display_current_model()
{
    print_sines_parameters
    awk 'NR > 1 {print $0}' ${MODEL_FILE}
    print_model_yintercept
    awk 'NR == 1 {print $0}' ${MODEL_FILE}
}

function display_frequencies()
{
    if [ -e ${MODEL_FILE} ]
    then
        awk 'NR > 1 {print $2}' ${MODEL_FILE}
    fi
}

function phase_lightcurve()
{
    local frequency

    print_choose_frequency
    display_frequencies
    print_hashbar
    read frequency

    phase.py ${lightcurve_filename} ${frequency} --model ${MODEL_FILE} $1
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

function change_fourier_parameters()
{
    set_fourier_parameter "FT_START"
    set_fourier_parameter "FT_STOP"
    set_fourier_parameter "FT_STEP"
}

function set_fourier_parameter()
{
    local parameter

    print_fourier_parameter $1
    read parameter

    if [ "${parameter}" != "" ]
    then
        eval $1=${parameter}
    fi
}

function save_results()
{
    local answer

    print_save_results
    print_question_about_variability

    while read answer
    do
        if [ "$answer" == "y" ]
        then
            print_phase_lightcurve
            save_all_results
            break
        elif [ "$answer" == "n" ]
        then
            log_constant_object
            break
        else
            print_question_about_variability
            continue
        fi
    done
}

function save_all_results()
{
    phase_lightcurve "--image"
    add_comment_to_log
    copy_results
}

function add_comment_to_log()
{
    local comment

    print_write_comment
    print_hashbar
    read comment
    echo -e "${lightcurve_filename}: ${comment}" >> ${RESULTS_DIR}/${RESULTS_LOG}
}

function copy_results()
{
    cp ${MODEL_FILE} ${RESULTS_DIR}/${lightcurve_filename/${LC_SUFFIX}/.mdl}
    mv ${lightcurve_filename/${LC_SUFFIX}/.png} ${RESULTS_DIR}/.
}

function log_constant_object()
{
    local comment="${lightcurve_filename}: constant"
    echo -e ${comment} >> ${RESULTS_DIR}/${RESULTS_LOG}
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

function clean_working_dir()
{
    restart_analysis
    remove_files_or_dirs ${lightcurve_filename}
}
