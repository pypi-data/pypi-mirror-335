#!/bin/env bash

# shellcheck source="/data/herman/Documents/Git Repositories/Herman Code/Shell Package/functions/functions.bash"
source "$HERMANS_CODE_INSTALL_PATH/Shell Package/functions/functions.bash"

usage0() {
    cat <<USAGE
WARNING THIS RESOURCE HAS NOT BEEN FULLY IMPLEMENTED YET.
    1. Test absolute and relative paths
    2. Confirm symoblic links are valid

$(basename "$0") -p <SOURCE> -d <TARGET>

    -p <SOURCE> is the file path(s) you want to link to.
    -d <TARGET> is the path to the directory you want to create the link in.
USAGE
}

usage() {
    usage0 1>&2
    exit 1
}

# >>> Argument parsing >>>
while getopts ":p:d:" opt; do
    case "${opt}" in
        # p) SOURCE+=("$OPTARG");;
        p) SOURCE=${OPTARG};;
        d) TARGET=${OPTARG};;
        *) usage;;
    esac
done
shift $((OPTIND -1))

if [ -z "${SOURCE}" ] || [ -z "${TARGET}" ]; then
    usage
fi
# <<< Argument parsing <<<

# >>> Argument confirmation >>>
SHOULD_EXIT=0

# $SOURCE
if [[ -z "$SOURCE" ]]; then
    echo "${RED}You must supply a keyword to search for${NC}."
    SHOULD_EXIT=1
fi

# $TARGET
if [[ -z "$TARGET" ]]; then
    echo "${RED}You must supply the directory path to search in${NC}."
    SHOULD_EXIT=1
fi

# Argument confirmation
# echo "SOURCE:"
# for val in "${TRACE_KEYWORDS[@]}"; do
#     echo "  - $val"
# done
echo "SOURCE = ${SOURCE}"
echo "TARGET = ${TARGET}"

if [ "$SHOULD_EXIT" -eq 0 ]; then
    :
else
    exit $SHOULD_EXIT
fi
# <<< Argument confirmation <<<

# Make Symlinks
# Method 1:
if [[ "$TARGET" = /* ]];
then
    if [[ "$SOURCE" = /* ]]; then
        echo "Mode 1: \`SOURCE\` is an absolute path."
        echo "        \`TARGET\` is an absolute path."
        # ls "$SOURCE" | xargs -I {} ln -sv "{}" "$TARGET/$(basename {})"  # old version
        ls "$SOURCE" | xargs -I {} bash -c 'ln -sv "{}" "$TARGET/$(basename "{}")"'  # new version
    else
        echo "Mode 2: \`SOURCE\` is a relative path."
        echo "        \`TARGET\` is an absolute path."
        # ls "$SOURCE" | xargs -I {} ln -sv "$(pwd)/{}" "$TARGET/$(basename {})"
        ls "$SOURCE" | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$TARGET/$(basename "{}")"'  # new version
    fi
else
    if [[ "$SOURCE" = /* ]]; then
        echo "Mode 3: \`SOURCE\` is an absolute path."
        echo "        \`TARGET\` is an relative path."
        # ls "$SOURCE" | xargs -I {} ln -sv "{}" "$(pwd)/$TARGET/$(basename {})"
        ls "$SOURCE" | xargs -I {} bash -c 'ln -sv "{}" "$(pwd)/$TARGET/$(basename "{}")"'  # new version
    else
        echo "Mode 4: \`SOURCE\` is a relative path."
        echo "        \`TARGET\` is an relative path."
        # ls "$SOURCE" | xargs -I {} ln -sv "$(pwd)/{}" "$(pwd)/$TARGET/$(basename {})"
        ls "$SOURCE" | xargs -I {} bash -c 'ln -sv "$(pwd)/{}" "$(pwd)/$TARGET/$(basename "{}")"'  # new version
    fi
fi
# Method 2. `SOURCE` must be relative, `TARGET` must be absolute

# Confirm Symlinks are valid TODO
if [[ "$OSTYPE" = "linux-gnu"* ]]; then
    ls -lashX "$TARGET"
elif [[ "$OSTYPE" = "darwin"* ]]; then
    ls -lash "$TARGET"
elif [[ "$OSTYPE" = "win32"* ]]; then
    :
else
    echo "Unsupported OS: \"$OSTYPE\""
fi
