# author: Zach Crabtree zacharyc@alleninstitute.org
# reworked by Jamie Sherman 20181112

import pytest
import numpy as np
import random
import os
import pathlib

from aicsimageio import AICSImage


class ImgContainer(object):
    def __init__(self, channels:int=5, dims:str="TCZYX"):
        self.input_shape = random.sample(range(1, 10), channels)
        stack = np.zeros(self.input_shape)
        self.dims = dims
        self.order =  {c:i for i,c in enumerate(dims)}  # {'T': 0, 'C': 1, 'Z': 2, 'Y': 3, 'X': 4}
        self.image = AICSImage(stack, dims=self.dims)

    def remap(self, seq):
        return [self.order[c] for c in seq]

    def shuffle_shape(self, seq):
        new_shape = [self.input_shape[self.order[c]] for c in seq]
        return tuple(new_shape)

    def get_trand_crand(self):
        tmax = 10


@pytest.fixture
def example_img5():
    return ImgContainer(5)


@pytest.fixture
def example_img3ctx():
    return ImgContainer(3, "CTX")


def test_helper_class(example_img5):
    assert example_img5.remap("XYZCT") == [4, 3, 2, 1, 0]


def test_transposed_output(example_img5):
    output_array = example_img5.image.get_image_data("XYZCT")
    stack_shape = example_img5.shuffle_shape("XYZCT")
    assert output_array.shape == stack_shape


def test_p_transpose(example_img5):
    output_array = AICSImage._AICSImage__transpose(example_img5.image.data, example_img5.dims, "YZXCT")
    stack_shape = example_img5.shuffle_shape("YZXCT")
    assert output_array.shape == stack_shape


def test_transposed_output_2(example_img5):
    order = "TCZYX"
    for _ in range(0, 20):
        new_order = ''.join(random.sample(order, len(order)))
        image = example_img5.image.get_image_data(new_order)
        shape = example_img5.shuffle_shape(new_order)
        assert image.shape == shape


def test_sliced_output():
    # arrange
    input_shape = random.sample(range(1, 20), 5)
    t_max, c_max = input_shape[0], input_shape[1]
    t_rand, c_rand = random.randint(0, t_max - 1), random.randint(0, c_max - 1)
    stack = np.zeros(input_shape)
    stack[t_rand, c_rand] = 1
    image = AICSImage(stack, dims="TCZYX")
    # act
    output_array = image.get_image_data("ZYX", T=t_rand, C=c_rand)
    # assert
    assert output_array.all() == 1
    assert stack[t_rand, c_rand, :, :, :].shape == output_array.shape


def test_few_dimensions(example_img3ctx):
    image = example_img3ctx.image
    assert image.data.shape == image.shape


def test_fromFileName():
    # arrange and act
    dir_path = os.path.dirname(os.path.realpath(__file__))
    image = AICSImage(os.path.join(dir_path, 'img', 'img40_1.ome.tif'))
    # assert
    assert image is not None


def test_fromInvalidFileName():
    # arrange, act, assert
    with pytest.raises(IOError):
        AICSImage("fakeimage.ome.tif")


def test_fromInvalidDataType():
    with pytest.raises(TypeError):
        AICSImage(pathlib.Path('foo.tiff'))
