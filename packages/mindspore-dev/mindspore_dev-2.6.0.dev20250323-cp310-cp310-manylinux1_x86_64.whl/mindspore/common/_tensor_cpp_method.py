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

tensor_cpp_methods = ['view_as', 'max', 't', 'floor_divide_', '__ifloordiv__', 'clamp', 'clip', 'prod', 'masked_select', 'isinf', 'narrow', 'exp_', 'addcdiv', 'tan', 'var', 'reciprocal', 'triu', 'bitwise_and', '__and__', 'sinh', 'gcd', 'scatter_add', 'neg', 'negative', 'mean', 'sub', '__sub__', 'sub_', '__isub__', 'add', '__add__', 'matmul', 'masked_fill', 'addmv', 'repeat_interleave', 'erfc', 'sqrt', 'copy_', 'addmm', 'nansum', 'lerp', 'index_add', 'transpose', 'addbmm', 'xlogy', 'asinh', 'arcsinh', 'subtract', 'isclose', 'asin', 'arcsin', 'unbind', 'any', 'div_', '__itruediv__', 'new_zeros', 'expand_as', 'argsort', 'tile', 'true_divide', 'diag', 'fill_', 'sinc', 'tril', 'type_as', 'scatter_', 'nan_to_num', 'unsqueeze', 'outer', 'mul_', '__imul__', 'dot', 'bitwise_or', '__or__', 'flatten', 'logaddexp', 'reshape', 'topk', 'repeat', 'frac', 'div', 'divide', 'clone', 'scatter', 'exp', 'atan2', 'arctan2', 'gather', 'greater', 'gt', 'index_select', 'hardshrink', 'logical_xor', 'remainder', 'less', 'lt', 'isneginf', 'argmin', 'not_equal', 'ne', 'roll', 'isfinite', 'where', 'std', 'mul', 'log10', 'greater_equal', 'ge', 'chunk', 'fill_diagonal_', 'ceil', 'logical_not', 'sin', 'log1p', 'select', 'sum', 'log', 'trunc', 'unique', 'sigmoid', 'less_equal', 'le', 'round', '_to', 'histc', 'cosh', 'sort', 'count_nonzero', 'allclose', 'median', 'logsumexp', 'maximum', 'pow', '__pow__', 'baddbmm', 'logical_or', 'atanh', 'arctanh', 'floor', 'cos', 'abs', 'absolute', '__abs__', 'log2', 'mm', 'min', 'add_', '__iadd__', 'take', 'log_', 'split', 'fmod', 'tanh', 'logaddexp2', 'kthvalue', 'put_', 'bitwise_not', 'bitwise_xor', '__xor__', 'masked_fill_', 'all', 'floor_divide', 'new_ones', 'acosh', 'arccosh', 'eq', 'acos', 'arccos', 'rsqrt', 'logical_and', 'expm1', 'minimum', 'cumsum', 'bincount', 'argmax', 'atan', 'arctan', 'erf', 'square', 'inverse']
