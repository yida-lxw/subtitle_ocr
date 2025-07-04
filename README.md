# subtitle-ocr

基于PaddleOCR实现智能识别视频帧图像上的字幕信息

### 环境安装
~~~shell
conda create -n subtitle-ocr3.10 python=3.10
conda activate subtitle-ocr3.10
~~~

### 依赖安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --verbose

### 安装 PanddleOCR
~~~shell
# for CUDA11.8
python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# for CUDA12.2
python -m pip install paddlepaddle-gpu==2.6.2.post120 -i https://www.paddlepaddle.org.cn/packages/stable/cu120/

# for CUDA12.6
python -m pip install paddlepaddle-gpu==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
~~~
> 对于英伟达显卡, 输入 nvidia-smi 确认当前显卡驱动CUDA版本, 国产NPU显卡需要自己进行源码编译


### 配置文件修改
  ~~~shell
  # 视频字幕提取服务的主机IP
  host: 192.168.0.106
  # 视频字幕提取服务监听的端口
  port: 8999
  # ffmpeg.exe的磁盘绝对路径
  ffmpeg_path: D:/ffmpeg-5.1.2/
  # 程序工作目录
  work_dir: D:/tmp/
  # PaddleOCR模型文件目录
  paddle_model_base_dir: D:/models/PaddlePaddle/
  # 使用的推理设备(cpu/gpu/npu)
  use_device: gpu
  # 是否全屏识别字幕, False=只识别图片底部的字幕, True=图片上任意位置出现的文本都识别为字幕
  use_fullframe: False
  # 是否启用字幕缓存
  enable_subtitle_cache: true
  ~~~
> 其他配置项保持默认即可, 或者你在熟知了各个配置项含义的情况下, 可自行酌情修改.

### 程序启动
> 注意: 启动之前,请先清空db.yml配置文件db-dir指向的数据库目录下的subtitle_ocr文件
~~~shell
#前台启动(Windows & Linux)
# Windows环境
uvicorn main:app --host 192.168.0.100 --port 8999 --reload --workers=1 

#Linux环境
gunicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 

# 后台启动(Linux)
nohup gunicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 &

# 启动后运行日志写入日志文件(Linux)
nohup gunicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 >> run.log 2>&1 &

# 启动后运行日志写入日志文件(Windows)
unicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 -c "accesslog='access.log',errorlog='error.log'"
~~~
> 注意: gunicorn开头的命令用于Linux环境, uvicorn开头的命令用于Windows环境.

### Windows后台运行Python程序

+ run.bat

~~~shell
@echo off
chcp 65001
call conda activate subtitle-extraction3.10
unicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=8 -c "accesslog='access.log',errorlog='error.log'"
~~~

+ start.bat

~~~shell
@echo off
chcp 65001
powershell.exe -command "& {Start-Process -WindowStyle hidden -FilePath './run.bat'}"
~~~

最后双击 start.bat 脚本, 即可后台启动Python程序.

### 查看程序进程

~~~shell
# Windows
tasklist | findstr "main.py"
tasklist | findstr "python"

# Linux
ps -ef | grep "main.py"
ps -ef | grep "python"
~~~

### 杀死程序进程

~~~shell
# Windows
taskkill  /F /T /pid xxxxx

# Linux
kill -9 xxxxx
~~~
