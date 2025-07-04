#!/bin/bash
# 设置UTF-8编码环境
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 参数检查
if [ $# -ne 5 ]; then
    echo "错误：参数数量不正确，需要5个参数："
    echo "用法：$0 <输入视频路径> <输出目录> <文件名前缀> <ffmpeg路径> <fps值>"
    exit 1
fi

input_file="$1"
output_dir="$2"
prefix="$3"
ffmpeg_path="$4"
fps="$5"

# 创建输出目录（若不存在）
mkdir -p "$output_dir${prefix}" || { echo "无法创建输出目录：$output_dir${prefix}"; exit 1; }

# 执行FFmpeg命令
"$ffmpeg_path" -i "$input_file" -vf "fps=$fps,drawtext=text='%%{pts\:hms}':fontsize=30:fontcolor=white:box=1:boxcolor=black@0.5:x=10:y=10" -q:v 3 -y "$output_dir${prefix}/${prefix}_%08d.jpg"
exit 0