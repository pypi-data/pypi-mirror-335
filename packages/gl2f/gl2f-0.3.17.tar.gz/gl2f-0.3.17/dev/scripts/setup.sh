sudo apt update && sudo apt install libsixel-bin -y
git submodule update --init --recursive
pip install -e .
eval "$(gl2f completion)"
