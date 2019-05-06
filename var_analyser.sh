#!/usr/bin/env bash

source ${VARANA_PATH}/lib/messages_lib.bash
source ${VARANA_PATH}/lib/var_lib.bash
source ${VARANA_PATH}/lib/filesys_lib.bash
source ${VARANA_PATH}/lib/prepare_lc_lib.bash


configure_file=${VARANA_PATH}/var.config

if [ $# -eq 1 ] || [ $# -eq 3 ]
then
    while [ $# -gt 0 ]
    do
        case $1 in
            --config)
                configure_file="$2"
                shift 2
                ;;
            *)
                lightcurve_file=$1
                lightcurve_filename=`basename $1`
                shift
                ;;
        esac
    done
else
    welcome_message
fi

check_whether_files_exist ${lightcurve_file} ${configure_file}
source ${configure_file}

create_not_existing_dir ${LC_DETREND_DIR} ${LC_TRIM_DIR} ${RESULTS_DIR}
detrend ${lightcurve_file}
trim ${lightcurve_file}
copy_lightcurve ${lightcurve_file} .
display_tasks
