#!/bin/bash
# Usage: ./genrpm.sh <version>

version=$1
# generate source tar
python setup.py sdist --formats=gztar
# copy it where rpmbuild specs it
mv dist/sugarlistens-${version}.tar.gz ~/rpmbuild/SOURCES/
# generate rpm package
rpmbuild -ba sugarlistens.spec

