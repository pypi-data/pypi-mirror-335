#!/bin/bash

bin=$(dirname "${BASH_SOURCE:-$0}")/../../bin
echo $bin

src="${bin}/main.py"
pyinstaller $src --onefile --name gl2f --collect-data gl2f
