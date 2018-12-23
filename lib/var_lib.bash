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
