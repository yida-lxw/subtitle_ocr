@echo off
chcp 65001 > nul

REM 检查是否传入输入文件参数
if "%1"=="" (
    echo 错误：未指定输入视频文件路径
    exit /b 1
)
if "%2"=="" (
    echo 错误：未指定JPG图片输出目录路径
    exit /b 1
)
if "%3"=="" (
    echo 错误：未指定JPG图片文件名前缀
    exit /b 1
)
if "%4"=="" (
    echo 错误：未指定ffmpeg命令路径
    exit /b 1
)
if "%5"=="" (
    echo 错误：未指定分割图片的fps参数
    exit /b 1
)
%4 -i "%1" -vf "fps=%5,drawtext=text='%%{pts\:hms}':fontsize=24:fontcolor=white:box=1:boxcolor=black@0.5:x=10:y=10" -q:v 3 -y "%2%3/%3_%%08d.jpg"
