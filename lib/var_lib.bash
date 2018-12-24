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
