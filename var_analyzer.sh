#!/usr/bin/env bash

source lib/messages_lib.bash
source lib/var_lib.bash


if [ $# -ne 1 ]
then
    welcome_message
else
    lightcurve_file=$1
fi

