# Define custom utilities for multibuild
# Test for OSX with [ -n "$IS_OSX" ]

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    :
}

function run_tests {
    # Runs tests on installed distribution from an empty directory
    # python --version
    # python -c 'import sys; import yourpackage; sys.exit(yourpackage.test())'
    :
}