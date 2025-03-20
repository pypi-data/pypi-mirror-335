import cv2


def add_border(img, border_size):
    bordered_img = cv2.copyMakeBorder(
        img,
        top=border_size,
        bottom=border_size,
        left=border_size,
        right=border_size,
        borderType=cv2.BORDER_CONSTANT,
    )
    return bordered_img
