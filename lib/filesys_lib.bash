function create_not_existing_dir()
{
    local dir

    for dir in "$@"
    do
        if [ ! -d $dir ]
        then
            mkdir $dir
        fi
    done
}

function remove_files_or_dirs()
{
    local item

    for item in "$@"
    do
        rm -rf $item
    done
}

function check_whether_files_exist()
{
    local item

    for item in "$@"
    do
        if [ ! -e ${item} ]
        then
            print_file_not_exists ${item}
            exit 1
        fi
    done
}
