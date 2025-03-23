from typing import Union, Tuple, Dict

from fvcore.nn.jit_analysis import JitModelAnalysis
from fvcore.nn.jit_handles import Handle
from torch import nn, Tensor

from .elem_count_handles import (
    addmm_elem_jit,
    bmm_elem_jit,
    conv_elem_jit,
    einsum_elem_jit,
    matmul_elem_jit,
    linear_elem_jit,
    norm_elem_jit,
    upsample_elem_jit,
    adaptive_avg_pool2d_elem_jit,
    grid_sampler_elem_jit
)

# A dictionary that maps supported operations to their flop count jit handles.
_DEFAULT_SUPPORTED_OPS: Dict[str, Handle] = {
    "aten::addmm": addmm_elem_jit,
    "aten::bmm": bmm_elem_jit,
    "aten::_convolution": conv_elem_jit,
    "aten::einsum": einsum_elem_jit,
    "aten::matmul": matmul_elem_jit,
    "aten::mm": matmul_elem_jit,
    "aten::linear": linear_elem_jit,
    # You might want to ignore BN elements due to inference-time fusion.
    # Use `set_op_handle("aten::batch_norm", None)
    "aten::batch_norm": norm_elem_jit,
    "aten::group_norm": norm_elem_jit,
    "aten::layer_norm": norm_elem_jit,
    "aten::instance_norm": norm_elem_jit,
    "aten::upsample_nearest2d": upsample_elem_jit,
    "aten::upsample_bilinear2d": upsample_elem_jit,
    "aten::adaptive_avg_pool2d": adaptive_avg_pool2d_elem_jit,
    "aten::grid_sampler": grid_sampler_elem_jit,
}

class ElemCountAnalysis(JitModelAnalysis):
    def __init__(
        self,
        model: nn.Module,
        inputs: Union[Tensor, Tuple[Tensor, ...]],
    ) -> None:
        super().__init__(model=model, inputs=inputs)
        self.set_op_handle(**_DEFAULT_SUPPORTED_OPS)

    __init__.__doc__ = JitModelAnalysis.__init__.__doc__
