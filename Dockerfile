FROM docker.m.daocloud.io/library/python:3.10

WORKDIR /app

## 设置 TZ 时区
ENV TZ=Asia/Shanghai


COPY requirements-docker.txt .

# 安装一系列的依赖
#RUN apt update
#RUN apt install curl -y --force-yes
RUN curl -L https://gitee.com/RubyMetric/chsrc/releases/download/v0.2.1/chsrc-x64-linux -o /usr/local/bin/chsrc && chmod +x /usr/local/bin/chsrc
RUN chsrc set debian tuna
RUN chsrc set python tuna
RUN apt install build-essential  libgl1-mesa-glx  libglib2.0-0 ffmpeg -y --force-yes

# 安装包
RUN pip install --no-cache-dir -r requirements-docker.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 单独安装torch paddleocr paddlepaddle-gpu 关联的(根据不同的系统下包 这里下的是gpu版本，测试机：CUDA=12.2)
RUN ARCH=$(dpkg --print-architecture) && echo "系统架构为: $ARCH" && \
    if [ "$ARCH" = "amd64" ]; then \
      echo "选择 amd64 版本的 PyTorch" &&\
      pip install torch==2.3.1+cu121 torchvision==0.18.1+cu121 torchaudio==2.3.1+cu121 --index-url https://download.pytorch.org/whl/cu121 && \
      pip install paddleocr==2.6.1.3 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
      pip install paddlepaddle-gpu==2.5.2.post120 -f https://www.paddlepaddle.org.cn/whl/linux/cudnnin/stable.html; \
    elif [ "$ARCH" = "arm64" ]; then \
      echo "选择 arm64 版本的 PyTorch" &&\
      pip install torchvision==0.20.0 torchaudio==2.5.1 -i https://pypi.tuna.tsinghua.edu.cn/simple; \
    else \
      echo "选择 未知 版本的 PyTorch" &&\
      pip install torch==2.3.1+cu121 torchvision==0.18.1+cu121 torchaudio==2.3.1+cu121 --index-url https://download.pytorch.org/whl/cu121 && \
      pip install paddleocr==2.6.1.3 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
      pip install paddlepaddle-gpu==2.5.2.post120 -f https://www.paddlepaddle.org.cn/whl/linux/cudnnin/stable.html; \
    fi
## 暴露端口
EXPOSE 8999

# 复制代码
COPY . .

## 启动项目
# CMD ["python", "./run.py"]
