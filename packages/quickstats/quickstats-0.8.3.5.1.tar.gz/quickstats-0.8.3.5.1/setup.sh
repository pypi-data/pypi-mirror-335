#!/bin/bash

DEFAULT_LCG_RELEASE="105c"

get_script_dir() {
    local SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
        local DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
        SOURCE="$(readlink "$SOURCE")"
        [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
    echo "$DIR"
}

find_lcg_versions() {
    local LCG_VERSION=$1

    # Get the machine architecture
    local ARCH=$(uname -m)

    # Convert architecture to match LCG subdirectory format
    case "$ARCH" in
        x86_64)
            ARCH="x86_64"
            ;;
        aarch64)
            ARCH="aarch64"
            ;;
        *)
            echo "Unsupported architecture: $ARCH"
            return 1
            ;;
    esac

    # Get the Linux distribution
    local DISTRO=""
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        # Extract the leading number from VERSION_ID
        local VERSION_MAJOR=${VERSION_ID%%.*}
        case "$ID" in
            centos)
                DISTRO="centos${VERSION_MAJOR}"
                ;;
            rhel|el|elma|almalinux)
                DISTRO="el${VERSION_MAJOR}"
                ;;
            *)
                echo "Unsupported Linux distribution: $ID" >&2
                return 1
                ;;
        esac
    else
        echo "Cannot determine Linux distribution." >&2
        return 1
    fi

    # Directory where LCG releases are stored
    local LCG_DIR="/cvmfs/sft.cern.ch/lcg/views/$LCG_VERSION"

    # Check if the directory exists
    if [ ! -d "$LCG_DIR" ]; then
        echo "LCG version $LCG_VERSION does not exist." >&2
        return 1
    fi

    # List and filter appropriate subdirectories
    local VALID_VERSIONS=$(ls -d "$LCG_DIR"/* | xargs -n 1 basename | grep -E "^$ARCH-$DISTRO-gcc[0-9]+-(opt|dbg)$")

    # If no valid versions are found, exit
    if [ -z "$VALID_VERSIONS" ]; then
        echo "No compatible versions found for architecture $ARCH and distribution $DISTRO." >&2
        return 1
    fi

    # Sort by GCC version (descending), then by type (opt first)
    local SORTED_VERSIONS=$(echo "$VALID_VERSIONS" | sort -t- -k3,3r -k4,4r -k4,4 -s)

    # Return the sorted versions
    echo "$SORTED_VERSIONS"
}

if [ -d "/afs/cern.ch" ]; then
  InLxplus=true
else
  InLxplus=false
fi

# check if inside SWAN setup
if [[ -z ${SWAN_HOME} && -z ${SWAN_ENV_FILE} && -z ${SWAN_LIB_DIR} ]]; then
    # use environment name given by user
    if [ "$#" -ge 1 ];
    then
        EnvironmentName=$1
    # fall back to lcg if inside lxplus
    elif [ "$InLxplus" ];
    then
        EnvironmentName="lcg"
    # fall back to slac if inside SLAC
    elif [ "$InSLAC" ];
    then
        EnvironmentName="slac"
    else
        EnvironmentName="default"
    fi

    export DIR=$(get_script_dir)
else
  EnvironmentName="swan"
  export DIR=$(dirname "$USER_ENV_SCRIPT")
fi

# more stack memory
ulimit -S -s unlimited

echo "Setting up environment: $EnvironmentName"

# custom environment
if [[ "$EnvironmentName" =~ ^(conda|default)$ ]];
then
    # change PATH_TO_CONDA_ENV to your own conda environment path
    export CONDA_ENV_PATH=/my/conda/env/path
    
    if [[ "$EnvironmentName" = "conda" ]];
    then
        source ${CONDA_ENV_PATH}/../../etc/profile.d/conda.sh
        CONDA_ENV_NAME=$(basename "${CONDA_ENV_PATH%/}")
        conda activate $CONDA_ENV_NAME
    fi
    export PATH=${CONDA_ENV_PATH}/bin:$PATH
    
elif [[ "$EnvironmentName" =~ ^(lcg|panda)$ ]]; 
then

    if [ "$#" -ge 2 ];
    then
        LCG_RELEASE=LCG_$2
    else
        LCG_RELEASE=LCG_$DEFAULT_LCG_RELEASE
    fi
    
    export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
    source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh

    LCG_VERSION=$(find_lcg_versions "$LCG_RELEASE" | head -n 1)

    if [ -z "$LCG_VERSION" ]; then
        echo "Failed to find suitable version for the LCG release: $LCG_RELEASE" >&2
        return 1
    fi
    
    lsetup "views $LCG_RELEASE $LCG_VERSION"

    if [[ "$EnvironmentName" = "panda" ]];
    then
        lsetup panda
        lsetup rucio
    fi
elif [[ "$EnvironmentName" = "swan" ]];
then
    :
fi

export PATH=${DIR}/bin:${PATH}
export PYTHONPATH=${DIR}:${PYTHONPATH}