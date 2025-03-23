import json

from fvcore.nn import FlopCountAnalysis
from tabulate import tabulate
import torch

from tensorscope import ElemCountAnalysis

# number of bytes in each element for each precision
PRECISION_TO_BYTES = {
    'fp64': 8, # FP64 true
    'fp32': 4, # FP32 true
    'fp16-mixed': 2, # FP16 AMP
    'fp16-true': 2, # FP16 true
    'bf16-mixed': 2, # BF16 AMP
    'bf16-true': 2 # BF16 true
}

# lowest precision normally supported for numerically unstable operations
OP_MIN_PRECISION = {
    'batch_norm': 'fp32', # norm layers usually stay in FP32
    'group_norm': 'fp32', # norm layers usually stay in FP32
    'layer_norm': 'fp32', # norm layers usually stay in FP32
    'instance_norm': 'fp32' # norm layers usually stay in FP32
}

def analyze_model(model: torch.nn.Module, input_shapes: list[tuple], gpu: str, precision: str) -> None:
    # read in JSON files containing GPU specs
    with open('./gpu_specs.json', 'r') as file:
        gpu_specs = json.load(file)
    
    inputs = tuple([torch.randn(shape) for shape in input_shapes])

    # ensure precision is recognized
    if precision not in PRECISION_TO_BYTES:
        raise ValueError(f'Unexpected precision value: {precision}')
    
    # analyze model for FLOP and elements read/written counts
    flops_analysis = FlopCountAnalysis(model, inputs)
    elems_analysis = ElemCountAnalysis(model, inputs)
    flops_total = flops_analysis.total()
    flops_by_module_and_operator = flops_analysis.by_module_and_operator()
    elems_total = elems_analysis.total()
    elems_by_module_and_operator = elems_analysis.by_module_and_operator()

    # report whole model info
    print(f'Total FLOPs: {flops_total}')
    print(f'Total elems: {elems_total}')
    
    # ensure the FLOP and element analyses contain the same number of modules
    if len(flops_by_module_and_operator) != len(elems_by_module_and_operator):
        raise ValueError(f'Expected number of keys to be equal, got {len(flops_by_module_and_operator)} and {len(elems_by_module_and_operator)}')

    data = []
    # iterate through each module
    for flop_module_key, elem_module_key in zip(flops_by_module_and_operator, elems_by_module_and_operator):
        # ensure the current module name in each analysis is the same
        if flop_module_key != elem_module_key:
            raise ValueError(f'Expected keys to be equal, got {flop_module_key} and {elem_module_key}')
        # skip model totals
        if flop_module_key == '':
            continue
        
        # ensure the current module has the same number of operations in each analysis
        if len(flops_by_module_and_operator[elem_module_key]) != len(elems_by_module_and_operator[elem_module_key]):
            raise ValueError(f'Expected Counters to be have equal length, got {len(flops_by_module_and_operator[flop_module_key])} and {len(elems_by_module_and_operator[elem_module_key])}')
        if flop_module_key != '' and (len(flops_by_module_and_operator[flop_module_key]) != 1 or len(elems_by_module_and_operator[elem_module_key]) != 1):
            continue
        
        # iterate through operation
        for flop_op_key, elem_op_key in zip(flops_by_module_and_operator[flop_module_key], elems_by_module_and_operator[elem_module_key]):
            # ensure the current operation name in each moduleis the same
            if flop_op_key != elem_op_key:
                raise ValueError(f'Expected keys to be equal, got {flop_op_key} and {elem_op_key}')
            
            # get byte count
            flops_count = flops_by_module_and_operator[flop_module_key][flop_op_key]
            elems_count = elems_by_module_and_operator[flop_module_key][elem_op_key]

            # get operation's bytes per element
            op_precision = precision
            bytes_per_elem = PRECISION_TO_BYTES[precision]
            # check if an operation does not actually cast to lower precisions
            if flop_op_key in OP_MIN_PRECISION and 'true' not in precision:
                if PRECISION_TO_BYTES[OP_MIN_PRECISION[flop_op_key]] > PRECISION_TO_BYTES[precision]:
                    op_precision = OP_MIN_PRECISION[flop_op_key]
                bytes_per_elem = PRECISION_TO_BYTES[op_precision]
            bytes_count = elems_count * bytes_per_elem

            # accumulate data
            arithmetic_intensity = flops_count / bytes_count
            gpu_ops_bytes_ratio = gpu_specs[gpu][op_precision.split('-')[0]] / (gpu_specs[gpu]['memory_bandwidth'] / 1000)
            limitation = 'Arithmetic' if arithmetic_intensity > gpu_ops_bytes_ratio else 'Memory'
            row_data = [flop_module_key, flop_op_key, op_precision.split('-')[0], flops_count, bytes_count, arithmetic_intensity, gpu_ops_bytes_ratio, limitation]
            data.append(row_data)

    # print data
    headers = ['Module', 'Op', 'Precision', 'FLOPs', 'Bytes', 'Arithmetic Intensity', 'GPU FLOPs:Bytes Ratio', 'Limitation']
    print(tabulate(data, headers))

    # calculate an estimated time for the forward pass
    # TODO This estimate is known to underestimate the actual type by as much as 20x or more.
    #      This is something to be further researched and improved.
    forward_time = 0
    for row in data:
        gpu_flops = gpu_specs[gpu][op_precision.split('-')[0]] * 1_000_000_000_000 # GPU FLOPS (FLOPs / second)
        gpu_mem_bw = gpu_specs[gpu]['memory_bandwidth'] * 1_000_000_000 # GPU bandwidth (bytes / second)
        forward_time += max(row[3] / gpu_flops, row[4] / gpu_mem_bw)
    print(f'Estimated forward pass: {forward_time}')
