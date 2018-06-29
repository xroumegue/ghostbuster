#! /bin/bash

# Neither undefined variables (-u) or error in command (-e) are allowed
set -eu;

PYTHON3="/usr/bin/python3.6"
PREFIX="$(pwd)/venv"
HELP=false
VERBOSE=false
PIP=pip3

while true;
do
    case "${1:-unset}" in
        -v | --verbose) VERBOSE=true; shift ;;
        -h | --help) HELP=true; shift ;;
        -p | --prefix) PREFIX=$(readlink -m "$2"); shift 2;;
        --python) PYTHON3=$(readlink -m "$2"); shift 2;;
        --)  shift; break ;;
        *) break ;;
    esac
done


function log {
    if $VERBOSE; then
        echo "$1"
    fi
}

function check_env {
    if [ ! -x "$PYTHON3" ];
    then
        echo "$PYTHON3" does not exit or is not executable
        echo 'sudo apt install python3.6'
        exit -1
    fi

    PYTHON3_VERSION=$($PYTHON3 --version |& cut -d ' ' -f2 | cut -d '.' -f1,2)
    if [[ ! $PYTHON3_VERSION =~ 3\.6 ]]
    then
        echo Only python 3.6 version is supported.
        echo 'sudo apt install python3.6'
        exit -1
    else
        echo python version $PYTHON3_VERSION is supported.
    fi

    if [ ! -x /usr/bin/pyvenv-${PYTHON3_VERSION} ];
    then
        echo python venv is missing !
        echo sudo apt install  python${PYTHON3_VERSION}-minimal python${PYTHON3_VERSION}-venv
        exit -1
    fi

    if [ ! /usr/bin/python${PYTHON3_VERSION}-config   ];
    then
        echo python dev is missing !
        echo sudo apt install  python${PYTHON3_VERSION}-dev
        exit -1
    fi


}


function help {
    cat <<EOF
NAME:
    $0 - Generate cst-py (python Code Signing Tool) environment

OPTIONS:
    --verbose: Generate more logs
    --help: This output message
    --prefix: Where to install the library and python environment
    --python: Python3 executable path
EOF
    exit 0
}
log "Prefix: $PREFIX"
log "Python: $PYTHON3"

if $HELP;
then
	help
fi

check_env

if [ ! -d "$PREFIX" ];
then
	log "Creating virtualenv folder..."
	mkdir -p "$PREFIX"
	log "Creating python3 virtualenv..."
	"$PYTHON3" -m venv "$PREFIX"
fi

if  [ ! -e $PREFIX/bin/activate ]
then
	log "Creating python3 virtualenv..."
	"$PYTHON3" -m venv "$PREFIX"
fi

log "Activating virtualenv..."

set +eu;
# shellcheck source=/dev/null
. "$PREFIX/bin/activate"
set -eu;

packages=(
"wheel"
"pandas"
"scikit-learn"
"scipy"
)

for package in "${packages[@]}"; do
    log "Installing $package"
	"$PIP" install "$package"
done
