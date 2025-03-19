import cv2
import numpy as np
image = cv2.imread('/Users/chujianfei/Downloads/beautiful-young-woman-black-coat-winter-glamour-37598 (1).png')
# 遍历所有像素点
for i in range(image.shape[0]):
    for j in range(image.shape[1]):
        # 获取当前像素点的RGB值
        b, g, r = image[i][j]

        # 对每个通道进行操作（这里只展示了BGR三个通道）
        new_b = int(b * 100)
        new_g = int(g * 100)
        new_r = int(r * 100)

        # 更新像素点的RGB值
        image[i][j] = [new_b, new_g, new_r]

# img = image.astype('float32')/255
# print(image.shape, image.size, image.dtype)
cv2.imwrite('/Users/chujianfei/Downloads/cjf-20241023-3.png', image)
