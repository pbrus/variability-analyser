function welcome_message()
{
    print_welcome
    exit 1
}

function rearrange_columns_lightcurve()
{
    awk '{
        print $'${LC_TIME_COLUMN}', $'${LC_MAG_COLUMN}', $'${LC_ERR_COLUMN}'
    }' $1 > $1.tmp
}
