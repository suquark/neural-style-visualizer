from __future__ import print_function
from os.path import exists
import numpy as np
from settings import img_width, img_height
from scipy.misc import imread, imresize, imsave


def preprocess_image(image_path):
    """
    util function to open, resize and format pictures into appropriate tensors
    :param image_path: PAth to read the image
    :return:
    """
    img = imresize(imread(image_path), (img_width, img_height))
    img = img.transpose((2, 0, 1)).astype('float64')
    img = np.expand_dims(img, axis=0)
    return img


def deprocess_image(x):
    """
    util function to convert a tensor into a valid image
    :param x: numpy array for image
    :return: a tuned array
    """
    x = x.transpose((1, 2, 0))
    x = np.clip(x, 0, 255).astype('uint8')
    return x


def random_image():
    """
    Create a random image
    :return: A random image
    """
    return np.random.uniform(0, 255, (1, 3, img_width, img_height))


def grey_image():
    """
    Create a random image
    :return: A random image
    """
    return np.ones((1, 3, img_width, img_height)) * 128.0


def img_in(content_path, style_path):
    content = preprocess_image(content_path)
    style = preprocess_image(style_path)
    return content, style


def img_save(x, fname, allow_override=False):
    """
    Save image
    :param x: numpy array of image
    :param fname: filename
    :param allow_override: if a image exist, override it only when it is necessary
    :return:
    """
    img = deprocess_image(x.reshape((3, img_width, img_height)))
    if not allow_override and exists(fname):
        raise Exception('Image exists')
    imsave(fname, img)
