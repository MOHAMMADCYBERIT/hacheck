#!/bin/bash
#
# This builds a statically linked binary for haupdown that
# has python and virtualenv etc. all in one binary. This is
# useful since we can in theory volume mount this binary
# into any docker container and run it, reducing the need
# for sidecars to run hacheck.
set -eu
rm -rf /work/hacheck/static
virtualenv -p python3.6 /static
set +u
source /static/bin/activate
set -u
pip install -r /work/requirements.txt
pip install pyinstaller staticx patchelf-wrapper
pyinstaller --onefile /work/hacheck/haupdown.py --distpath /work/hacheck/static/
staticx /work/hacheck/static/haupdown /work/hacheck/static/haupdown_static
rm -f /work/hacheck/static/haupdown && mv /work/hacheck/static/haupdown_static /work/hacheck/static/haupdown
