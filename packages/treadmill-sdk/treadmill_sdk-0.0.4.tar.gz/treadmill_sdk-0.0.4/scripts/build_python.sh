#!/bin/bash
set -e

# colorful echo functions
function echo_y() { echo -e "\033[1;33m$@\033[0m"; } # yellow
function echo_r() { echo -e "\033[0;31m$@\033[0m"; } # red

# 获取脚本所在目录
SCRIPT_DIR="$(dirname $0)"

# 切换到脚本所在目录（如果当前目录不是脚本所在目录）
[ "$(pwd)" != "$SCRIPT_DIR" ] && cd "$SCRIPT_DIR"
echo_y "current dir: $(pwd)"

cd ..

cargo fmt

function load_pyenv() {
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
}
if [ "$(uname)" == "Darwin" ]; then
  load_pyenv
fi
# if not exists venv3_10, create it
# pyenv virtualenv venv3_10

# pyenv activate venv3_10
# pyenv shell venv3_10
# pyenv local venv3_10
# pyenv global venv3_10
python -V
which python
maturin dev --no-default-features --features "python"

cargo fmt

# if [ -z "$GITHUB_ACTIONS" ]; then
#   sh scripts/run_python.sh
# fi

# ln -sfv "$(pwd)/examples/python/tml_mock_data.dat" examples/encrypt
export PATH="/Users/brain-mini/.pyenv/versions/3.10.15/envs/venv3_10/bin:$PATH"
