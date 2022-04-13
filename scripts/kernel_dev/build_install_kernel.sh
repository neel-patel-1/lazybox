#!/bin/bash

set -e

if [ $# -ne 2 ] && [ $# -ne 3 ]
then
	echo "Usage: $0 <src dir> <build dir> [config file to append]"
	exit 1
fi

bindir=$(dirname "$0")
src_dir=$1
build_dir=$2

if [ $# -eq 3 ]
then
	additional_config_file=$3
fi

orig_config=$build_dir/.config

if [ ! -d "$build_dir" ]
then
	mkdir "$build_dir"
fi

if [ ! -f "$orig_config" ]
then
	cp "/boot/config-$(uname -r)" "$orig_config"
fi

if [ ! "$additional_config_file" = "" ]
then
	cat "$additional_config_file" >> "$build_dir/.config"
fi

make -C "$src_dir" O="$build_dir" olddefconfig
make -C "$src_dir" O="$build_dir" -j$(nproc)
sudo make -C "$src_dir" O="$build_dir" modules_install install
kernelversion=$(make -C "$src_dir" O="$build_dir" -s kernelrelease)
sudo "$bindir/set_kernel.py" "$kernelversion"