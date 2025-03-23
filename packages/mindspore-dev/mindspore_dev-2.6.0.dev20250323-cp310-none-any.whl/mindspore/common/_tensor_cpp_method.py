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

tensor_cpp_methods = ['bitwise_or', '__or__', 'exp_', 'sub', '__sub__', 'fill_diagonal_', 'fmod', 'index_select', 'prod', 'mul_', '__imul__', 'erfc', 'transpose', 'scatter_add', 'mul', 'masked_select', 'div_', '__itruediv__', 'addmm', 'chunk', 'count_nonzero', 'atan', 'arctan', 'logical_or', 'new_zeros', 'unsqueeze', 'logsumexp', 'floor_divide_', '__ifloordiv__', 'tril', 'isfinite', 'scatter', 'logical_not', 'pow', '__pow__', 'view_as', 'matmul', 'all', 'floor', 'greater_equal', 'ge', 'hardshrink', 'reciprocal', 'ceil', 'argmax', 'add_', '__iadd__', 'where', 'neg', 'negative', 'addmv', 'inverse', 'acos', 'arccos', 'subtract', 'unique', 'allclose', 'isinf', 'reshape', 'round', 'logaddexp2', 'minimum', 'sqrt', 'median', 'tile', 'rsqrt', 'exp', 'logical_and', 'less', 'lt', 'gather', 'scatter_', 'erf', 'clamp', 'clip', 'atanh', 'arctanh', 'index_add', 'max', 'sort', 'less_equal', 'le', 'tanh', 'not_equal', 'ne', 'atan2', 'arctan2', 'remainder', 'asin', 'arcsin', 'kthvalue', 'diag', 'topk', 'log10', 'masked_fill_', 'mm', 'bitwise_and', '__and__', 'abs', '__abs__', 'absolute', 'repeat_interleave', 'sin', 'repeat', 'sub_', '__isub__', 'trunc', 'expand_as', 'argsort', 'frac', 'maximum', 'log1p', 'addcdiv', 'cos', 'square', 'tan', 'bincount', 'xlogy', 'any', 'outer', 'clone', 'addbmm', 'true_divide', 'isneginf', 'nan_to_num', 'min', 'log_', 'type_as', 'select', 'sum', 'asinh', 'arcsinh', 'std', 'masked_fill', 'roll', 'fill_', 'bitwise_xor', '__xor__', 'log2', '_to', 'log', 'narrow', 'copy_', 'greater', 'gt', 'sinh', 'cumsum', 'baddbmm', 'new_ones', 'lerp', 'isclose', 'sinc', 'dot', 'split', 'triu', 't', 'cosh', 'bitwise_not', 'floor_divide', 'histc', 'mean', 'sigmoid', 'take', 'div', 'divide', 'argmin', 'logical_xor', 'put_', 'var', 'gcd', 'add', '__add__', 'nansum', 'acosh', 'arccosh', 'logaddexp', 'eq', 'expm1', 'flatten', 'unbind']
