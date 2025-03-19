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
SRC="../android/myapplication/"
DST="../../treadmill-example/android"

echo_y "Source directory: $SRC"
echo_y "Destination directory: $DST"

cp -rf "$SRC/myapplication" "$DST/"

# 更新 download-lib.sh 中的版本号
CARGO_PKG_VERSION=$(grep '^version =' Cargo.toml | awk -F'"' '{print $2}')
echo_y "Cargo.toml version: $CARGO_PKG_VERSION"
sed -i '' "s/LIB_VERSION=\"v[0-9]*\.[0-9]*\.[0-9]*\"/LIB_VERSION=\"v${CARGO_PKG_VERSION}\"/g" "$SCRIPT_DIR/download-lib.sh"
echo_y "download-lib.sh version updated"
cp -f "$SCRIPT_DIR/download-lib.sh" $DST

# 批量复制文件
for dir in linux mac; do
  # 创建目标目录(如果不存在)
  # mkdir -p "$DST/$dir"

  # 复制下载脚本
  # cp -f "$SCRIPT_DIR/download-lib.sh" "$DST/$dir"

  # 复制源文件和Makefile
  cp -f "$SRC/$dir/"*.cpp "$DST/$dir/"
  cp -f "$SRC/$dir/Makefile" "$DST/$dir/"
done

# 单独复制multi_stark_example.cpp到linux目录
cp -rf "$SRC/mac/stark_multi_example.cpp" "$DST/linux/"

echo "copy python example"
SRC="examples/python"
DST_ROOT="$HOME/projects/stark-serialport-example/python"
DST="$DST_ROOT/modbus_example"
echo_y "python Source directory: $SRC"
echo_y "python Destination directory: $DST"

# 更新 requirements.txt 中的版本号
CARGO_PKG_VERSION=$(grep '^version =' Cargo.toml | awk -F'"' '{print $2}')
echo_y "Cargo.toml version: $CARGO_PKG_VERSION"
sed -i '' "s/bc_device_sdk==[0-9]*\.[0-9]*\.[0-9]*/bc_device_sdk==$CARGO_PKG_VERSION/g" $SRC/requirements-stark.txt
echo_y "requirements.txt updated"
# exit 0

cp -vf $SRC/requirements-stark.txt $DST_ROOT/requirements.txt
cp -vf $SRC/logger.py $DST
cp -vf $SRC/utils.py $DST
cp -vf $SRC/stark_*.py $DST/

echo "done"
