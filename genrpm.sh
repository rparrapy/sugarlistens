#!/bin/bash
# Usage: ./genrpm.sh <version>

version=$1
SPEC_DIR=packaging
# generate source tar
python setup.py sdist --formats=gztar
# copy it where rpmbuild specs it
mv dist/sugarlistens-${version}.tar.gz ~/rpmbuild/SOURCES/
# generate rpm package
rpmbuild -ba $SPEC_DIR/sugarlistens.spec

