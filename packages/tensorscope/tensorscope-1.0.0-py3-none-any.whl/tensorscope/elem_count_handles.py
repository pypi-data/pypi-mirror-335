import typing
from collections import Counter
from numbers import Number
from typing import Any, List

from fvcore.nn.jit_handles import get_shape
import torch

try:
    from math import prod
except ImportError:
    from numpy import prod


def addmm_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::addmm (matrix multiply and add)
    out = beta * input + alpha * (mat1 @ mat2)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # mat1
    elem_count += prod(get_shape(inputs[2])) # mat2
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def bmm_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::bmm (batched matrix multiply)
    out = input @ mat1
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # mat1
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def conv_elem_jit(inputs: List[Any], outputs: List[Any]) -> typing.Counter[str]:
    """
    Count elements read/written for atte::conv (convolution)
    out = conv(input, weight, bias)
    bias is optional
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # weight
    if not isinstance(inputs[2].type(), torch.NoneType):
        elem_count += prod(get_shape(inputs[2])) # bias
    elem_count += prod(get_shape(outputs[0])) # out
    return Counter({'conv': elem_count})


def einsum_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten:einsum (Einstein summation)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def matmul_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::matmul (matrix multiply)
    out = input @ mat1
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # weight
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def linear_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::linear (linear)
    out = input @ weight.T + bias
    bias is optional
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # weight
    if not isinstance(inputs[2].type(), torch.NoneType):
        elem_count += prod(get_shape(inputs[2]))  # bias
    elem_count += prod(get_shape(outputs[0]))  # out
    return elem_count


def norm_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for:
        aten::batch_norm (batch norm)
        aten::group_norm (group norm)
        aten::layer_norm (layer norm)
        aten::instance_norm (instance norm)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def upsample_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for:
        aten::upsample_nearest2d (upsample using nearest 2D)
        aten::upsample_bilinear2d (upsample using bilinear 2D)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def adaptive_avg_pool2d_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::adaptive_avg_pool2d (Adaptive Average Pooling 2D)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count


def grid_sampler_elem_jit(inputs: List[Any], outputs: List[Any]) -> Number:
    """
    Count elements read/written for aten::grid_sampler (Grid Sampling)
    """
    elem_count = 0
    elem_count += prod(get_shape(inputs[0])) # input
    elem_count += prod(get_shape(inputs[1])) # grid
    elem_count += prod(get_shape(outputs[0])) # out
    return elem_count
