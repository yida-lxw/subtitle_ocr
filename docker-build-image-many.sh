echo "Deploying application..."
# 定义一些参数
DOCKER_REGISTRY=xxxxxx:5555
BUILD_NAME=ocrbuilder-tmp
IMAGE_NAME=subtitle-ocr
# 版本控制（这个版本号拿来做多平台不与之前的冲突）
IMAGE_TAG=1.0.0-many

docker login -u docker -p docker ${DOCKER_REGISTRY}
docker buildx create --use --name ${BUILD_NAME}  \
    --config=buildkit.toml

echo build start: ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}
docker buildx build  \
        --build-arg IMAGE_TAG=${IMAGE_TAG}  \
        --builder ${BUILD_NAME}  \
        --platform linux/amd64,linux/arm64  \
        -t ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}  \
        -f Dockerfile  \
        .  \
        --push
echo build complate: ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}

docker buildx rm ${BUILD_NAME}
echo "done...."