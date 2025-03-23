# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Add tensor cpp methods for stub tensor"""

tensor_cpp_methods = ['neg', 'negative', 'asin', 'arcsin', 'isfinite', 'sinh', 'clone', 'expm1', 'mul', 'eq', 'logsumexp', 'roll', 'greater_equal', 'ge', 'reshape', 'min', 'any', 'std', 't', 'isinf', 'matmul', 'fmod', 'log_', 'index_add', 'fill_', 'unique', 'sum', 'triu', 'repeat_interleave', 'scatter_add', 'remainder', 'abs', '__abs__', 'absolute', 'isneginf', 'sub', '__sub__', 'lerp', 'frac', 'mm', 'isclose', 'addcdiv', 'add_', '__iadd__', 'logical_xor', 'subtract', 'all', 'repeat', 'split', 'not_equal', 'ne', 'bitwise_not', 'logical_not', 'bitwise_or', '__or__', 'maximum', 'addbmm', 'atanh', 'arctanh', 'chunk', 'argsort', 'rsqrt', 'fill_diagonal_', 'put_', 'div_', '__itruediv__', 'bitwise_and', '__and__', 'floor', 'log2', 'round', 'type_as', 'trunc', 'kthvalue', 'gcd', 'logical_or', 'topk', 'acosh', 'arccosh', 'erf', 'logical_and', 'scatter_', 'var', 'reciprocal', 'tril', 'dot', 'asinh', 'arcsinh', 'inverse', 'greater', 'gt', 'outer', 'count_nonzero', 'histc', 'div', 'divide', 'mul_', '__imul__', 'ceil', 'take', 'tanh', 'gather', 'square', 'allclose', 'acos', 'arccos', 'where', 'exp_', 'view_as', 'minimum', 'less', 'lt', 'scatter', 'sqrt', 'addmv', 'max', 'cumsum', 'cosh', 'mean', '_to', 'true_divide', 'log10', 'add', '__add__', 'diag', 'narrow', 'atan', 'arctan', 'masked_select', 'median', 'hardshrink', 'sinc', 'clamp', 'clip', 'argmin', 'cos', 'prod', 'atan2', 'arctan2', 'floor_divide_', '__ifloordiv__', 'xlogy', 'sort', 'logaddexp', 'transpose', 'less_equal', 'le', 'floor_divide', 'select', 'sin', 'exp', 'unbind', 'new_ones', 'sub_', '__isub__', 'new_zeros', 'masked_fill_', 'nan_to_num', 'tile', 'bitwise_xor', '__xor__', 'addmm', 'log1p', 'erfc', 'bincount', 'tan', 'pow', '__pow__', 'sigmoid', 'flatten', 'expand_as', 'baddbmm', 'index_select', 'copy_', 'logaddexp2', 'unsqueeze', 'argmax', 'masked_fill', 'nansum', 'log']
