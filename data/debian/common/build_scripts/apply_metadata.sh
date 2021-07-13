#!/bin/bash
# Copyright (c) 2021 Wind River Systems, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
set -x
set -e
source_dir=$1
if [ -z "$source_dir" -o ! -d "$source_dir" ]; then
    source_dir=${PWD}/workdir
fi

rm -rf ${source_dir}
mkdir -p ${source_dir}
cd ${source_dir}

metadata_dir="`dirname ${BASH_SOURCE[0]}`"
metadata_dir="`realpath ${metadata_dir}/../metadata`"
cp -rf ${metadata_dir}/* $source_dir/
