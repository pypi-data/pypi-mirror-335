import cv2
import numpy as np

# np.set_printoptions(threshold=64)
img_char = cv2.imread('./font_images64/2A1F8.png', 0)
img_char = img_char/255.
# print(img_char/255)
for i_vacter in img_char:
    for j in i_vacter:
        print(j, end=' ')
    print('\n')