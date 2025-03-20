import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from optical_toolkit.utils import add_border, preprocess


def visualize_images(images, y=None, image_size=200, border_size=0, fname="sprite.png"):
    """Create a sprite image from input data."""
    images = [cv2.resize(img, (image_size, image_size)) for img in images]
    images = preprocess(images)

    if border_size:
        images = [add_border(img, border_size) for img in images]

    images = np.array(images)

    sprite_image = create_sprite_image(images, y)

    output_path = os.path.join("examples", fname)
    plt.imsave(output_path, sprite_image)

    return sprite_image


def create_sprite_image(images, y):
    """Create a sprite image from a list of images."""
    if len(images.shape) == 4:
        channels = 3
    elif len(images.shape) == 3:
        images = np.expand_dims(images, axis=-1)
        channels = 1
    else:
        raise ValueError("Expected images of HxWxC (RGB) or HxW (Grayscale)")

    img_h, img_w = images.shape[1], images.shape[2]
    n_plots = int(np.floor(np.sqrt(images.shape[0])))
    sprite_image = np.ones((img_h * n_plots, img_w * n_plots, channels))

    for i in range(n_plots):
        for j in range(n_plots):
            curr_filter = i * n_plots + j
            if curr_filter < images.shape[0]:
                curr_img = images[curr_filter]
                sprite_image[
                    i * img_h : (i + 1) * img_h,
                    j * img_w : (j + 1) * img_w,
                ] = curr_img

                if y is not None:
                    label = str(y[curr_filter])
                    text_position = (j * img_w + 5, i * img_h + 20)
                    cv2.putText(
                        sprite_image,
                        label,
                        text_position,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0),
                        2,
                    )

    return np.clip(sprite_image, 0, 1)


__all__ = [visualize_images]
