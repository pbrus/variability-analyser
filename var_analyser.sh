#!/usr/bin/env bash

source lib/messages_lib.bash
source lib/var_lib.bash
source lib/filesys_lib.bash
source lib/prepare_lc_lib.bash
source var.config


if [ $# -ne 1 ]
then
    welcome_message
else
    lightcurve_file=$1
fi

create_not_existing_dir ${LC_DETREND_DIR} ${LC_TRIM_DIR}
detrend ${lightcurve_file}
trim ${lightcurve_file}
