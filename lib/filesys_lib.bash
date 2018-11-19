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
