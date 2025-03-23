import os

import cv2


def resize_image_smaller(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.jpg') or filename.endswith('.png') or filename.endswith('.JPEG'):
            filepath = os.path.join(folder_path, filename)
            img = cv2.imread(filepath)
            resized_img = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            cv2.imwrite(filepath, resized_img)


path = '../data/MSTAR/BRDM_2'  # 替换为你的文件夹路径
resize_image_smaller(path)
