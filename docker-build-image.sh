echo "Deploying application..."
DOCKER_REGISTRY=demo.witarchive.com:5555
IMAGE_NAME=subtitle-ocr
# 版本控制
IMAGE_TAG=1.0.0

docker login -u docker -p docker ${DOCKER_REGISTRY}

echo build start: ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}
docker build -t ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG} .
echo push start: ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}
docker push ${DOCKER_REGISTRY}/py-pro/${IMAGE_NAME}:${IMAGE_TAG}
echo "done...."