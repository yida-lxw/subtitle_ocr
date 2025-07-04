import os
import random
import shutil

"""
数据集划分
"""
def filter_files(directory, extension):
    # 获取目录下的所有文件和子目录
    files = os.listdir(directory)

    # 过滤出指定扩展名的文件
    filtered_files = [file for file in files if file.endswith(extension)]
    return filtered_files

def del_file(filepath):
    dir_exists = os.path.exists(filepath)
    if(dir_exists):
        del_list = os.listdir(filepath)
        for f in del_list:
            file_path = os.path.join(filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        #os.remove(filepath)


def splitDataSet(actionTypes, dataset_basepath, dataset_voc_basepath, radio: float = 0.80):
    # actionTypes = [ "burn-paper", "copy-write", "phone-call", "plug-in-usb",
    #                "pour-water", "smoke", "take-photo", "tear-paper"]

    # actionTypes = ["classified"]
    # dataset_basepath = "E:/SM_Images_Labeled_Merged/"
    # dataset_voc_basepath = "E:/voc/"

    for actionType in actionTypes:
        image_type = ".jpg"
        image_type_upercase = ".JPG"

        # 设置数据集路径
        dataset_path = dataset_basepath + "{actionTypeName}/".format(actionTypeName=actionType)
        dataset_voc_path = dataset_voc_basepath + "{actionTypeName}/".format(actionTypeName=actionType)
        images_path = os.path.join(dataset_path, "images")
        labels_path = os.path.join(dataset_path, "labels")

        # 创建训练集和验证集目录
        train_path = os.path.join(dataset_voc_path, "train")
        val_path = os.path.join(dataset_voc_path, "val")
        os.makedirs(train_path, exist_ok=True)
        os.makedirs(val_path, exist_ok=True)

        # 获取所有图像和标签文件的路径
        images = filter_files(images_path, ".jpg")
        labels = filter_files(labels_path, ".txt")

        # 确保图像和标签文件数量一致
        assert len(images) == len(labels)

        # 将文件名列表随机排序
        random.shuffle(images)

        # 计算训练集和验证集的数量
        train_size = int(radio * len(images))
        val_size = len(images) - train_size

        # 创建训练集和验证集目录
        train_path = os.path.join(dataset_voc_path, "train")
        del_file(train_path)
        train_images_path = os.path.join(train_path, "images")
        train_labels_path = os.path.join(train_path, "labels")
        os.makedirs(train_images_path, exist_ok=True)
        os.makedirs(train_labels_path, exist_ok=True)

        val_path = os.path.join(dataset_voc_path, "val")
        del_file(val_path)
        val_images_path = os.path.join(val_path, "images")
        val_labels_path = os.path.join(val_path, "labels")
        os.makedirs(val_images_path, exist_ok=True)
        os.makedirs(val_labels_path, exist_ok=True)

        # 复制训练集图像和标签文件到train目录
        for i in range(train_size):
            image_name = images[i]
            image_name = image_name.replace(image_type_upercase, image_type)
            label_name = image_name.replace(image_type, ".txt")
            src_image = os.path.join(images_path, image_name)
            src_label = os.path.join(labels_path, label_name)
            dst_image = os.path.join(train_images_path, image_name)
            dst_label = os.path.join(train_labels_path, label_name)
            shutil.copyfile(src_image, dst_image)
            shutil.copyfile(src_label, dst_label)

        # 复制验证集图像和标签文件到val目录
        for i in range(train_size, len(images)):
            image_name = images[i]
            label_name = image_name.replace(image_type, ".txt")
            src_image = os.path.join(images_path, image_name)
            src_label = os.path.join(labels_path, label_name)
            dst_image = os.path.join(val_images_path, image_name)
            dst_label = os.path.join(val_labels_path, label_name)
            shutil.copyfile(src_image, dst_image)
            shutil.copyfile(src_label, dst_label)

        print("[{action_type}]数据集已成功划分为训练集和验证集！".format(action_type=actionType))


if __name__ == '__main__':
    actionTypes = ["subtitle"]
    dataset_basepath = "D:/tmp/已标注/voc2/"
    dataset_voc_basepath = "D:/tmp/已标注/voc/"
    radio = 0.80
    splitDataSet(actionTypes, dataset_basepath, dataset_voc_basepath, radio=radio)
