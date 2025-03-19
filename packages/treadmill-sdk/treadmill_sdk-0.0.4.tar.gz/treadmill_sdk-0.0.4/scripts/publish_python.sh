# function load_pyenv() {
#   eval "$(pyenv init -)"
#   eval "$(pyenv virtualenv-init -)"
# }
# load_pyenv
# pyenv activate venv3_10

# export PYTHON=$(pyenv which python3.10)
# cibuildwheel --output-dir dist

# pip install cibuildwheel
# export CIBW_SKIP=cp38-*
# export CIBW_BUILD=cp10-*,cp11-*
# export CIBW_BUILD=cp310-macosx_*,cp311-macosx_*
# cibuildwheel --output-dir dist --debug-traceback
# maturin publish --skip-existing

# cargo fmt
# # maturin publish --username <your-username> --password <your-password> --features ""eeg-cap", "python""
maturin publish --no-default-features --features ""python"
