import numpy as np


def stitched_image(images, num_images, img_sz):
    margin = 5
    n = int(num_images ** (1 / 2))

    cropped_width = img_sz - 25 * 2
    cropped_height = img_sz - 25 * 2

    width = n * cropped_width + (n - 1) * margin
    height = n * cropped_height + (n - 1) * margin

    stitched_image = np.zeros((width, height, 3))

    for i in range(n):
        for j in range(n):
            image = images[i * n + j]
            stitched_image[
                (cropped_width + margin) * i: (cropped_width + margin) * i
                + cropped_width,
                (cropped_height + margin) * j: (cropped_height + margin) * j
                + cropped_height,
                :,
            ] = image

    return stitched_image


def concat_images(images, axis=1):
    margin = 5
    images = [np.asarray(img) for img in images]

    # Ensure all images have the same number of channels
    max_channels = max(img.shape[-1] if img.ndim == 3 else 1 for img in images)
    images = [
        img if (img.ndim == 3 and img.shape[-1] ==
                max_channels) else np.dstack([img] * max_channels)
        for img in images
    ]

    # Add margin between images horizontally or vertically
    if axis == 1:  # Horizontal concatenation
        padded_images = []
        for img in images:
            if len(img.shape) == 2:  # If grayscale, convert to 3 channels
                img = np.stack([img] * 3, axis=-1)
            # Add margin by padding to the right
            padded_image = np.pad(img, ((0, 0), (0, margin), (0, 0)),
                                  mode='constant', constant_values=0)
            padded_images.append(padded_image)
        return np.concatenate(padded_images, axis=1)

    elif axis == 0:  # Vertical concatenation
        padded_images = []
        for img in images:
            if len(img.shape) == 2:  # If grayscale, convert to 3 channels
                img = np.stack([img] * 3, axis=-1)
            # Add margin by padding to the bottom
            padded_image = np.pad(img, ((0, margin), (0, 0), (0, 0)),
                                  mode='constant', constant_values=0)
            padded_images.append(padded_image)
        return np.concatenate(padded_images, axis=0)
