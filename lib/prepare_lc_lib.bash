function rearrange_columns_lightcurve()
{
    awk '{
        printf("%f %f %f\n", $'${LC_TIME_COLUMN}'-'${LC_TIME_PREFIX}', \
        $'${LC_MAG_COLUMN}', $'${LC_ERR_COLUMN}')
    }' $1 > $1.tmp
}

function display_detrend_data()
{
    local output_file=${1/${LC_DIR}/${LC_DETREND_DIR}}

    detrend.py $1 ${output_file%".tmp"} $2 --display
}

function save_detrend_data()
{
    local output_file=${1/${LC_DIR}/${LC_DETREND_DIR}}

    detrend.py $1 ${output_file%".tmp"} $2 --image
}

function detrend_data()
{
    local nodes_number=9
    local answer="n"

    echo "Is OK? [y/n]:"
    display_detrend_data $1 ${nodes_number}
    read answer

    while [ "$answer" == "n" ]
    do
        echo "Number of nodes (last ${nodes_number}):"
        read nodes_number
        echo "Is OK? [y/n]:"
        display_detrend_data $1 ${nodes_number}
        read answer
    done

    save_detrend_data $1 ${nodes_number}
}

function detrend()
{
    if [ ! -e ${1/${LC_DIR}/${LC_DETREND_DIR}} ]
    then
        rearrange_columns_lightcurve $1
        detrend_data $1.tmp
        remove_files_or_dirs $1.tmp
    fi
}

function trim()
{
    if [ ! -e ${1/${LC_DIR}/${LC_TRIM_DIR}} ]
    then
        trim.py ${1/${LC_DIR}/${LC_DETREND_DIR}} \
        ${1/${LC_DIR}/${LC_TRIM_DIR}} --display --image
    fi
}
