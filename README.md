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
> 注意: <br/> gunicorn开头的命令用于Linux环境, uvicorn开头的命令用于Windows环境.<br/>另外，启动时， 若控制台打印出类似如下警告信息:<br/>UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)<br/>则需要执行 conda install -c conda-forge ccache 命令安装ccache<br/>

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

# 使用docker-compose部署项目流程：
```text
构建：（注意pytorch与CUDA版本匹配问题-若部署服务器不适配请修改或重制Dockerfile重新构建镜像，测试机CUDA=12.2）
特别注意：paddleocr包与paddlepaddle-gpu包的版本冲突，及与机器的CUDA匹配问题
1.将项目代码复制到构建服务器
2.执行构建命令
构建项目镜像（执行）：docker-build-image.sh(单平台，构建服务器决定)（已构建版本linux/amd64，修改代码后需要执行,注意版本控制）
构建项目镜像（执行）：docker-build-image-many.sh(多平台暂不支持，原因：paddleocr、paddlepaddle-gpu均不支持arm架构，实在需要请通过源码编译的方式在ARM架构上安装)
（已构建版本无(未测试)，修改代码后需要执行,注意版本控制）

部署：（创建文件夹或文件可以不必按照下面要求的级别，修改docker-compose.yml挂载的路径就行）
1. 在服务器与docker-compose.yml同级别创建包config复制配置文件并修改config/app.yml 、config/db.yml
2. 在服务器与docker-compose.yml同级别创建包.paddleocr用于存放项目其他依赖(一般启动会自动下载，没网的就自己下载好放进去)：.paddleocr/whl/cls/**、.paddleocr/whl/det/**、.paddleocr/whl/rec/**
3. 在服务器与docker-compose.yml同级别创建包models用于存放项目使用的第三方模型：PaddlePaddle/**
4. 到服务器路径下执行命令： docker compose up -d 或 docker-compose up -d
```