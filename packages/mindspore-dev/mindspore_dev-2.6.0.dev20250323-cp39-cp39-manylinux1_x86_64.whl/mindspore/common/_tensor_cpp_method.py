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

tensor_cpp_methods = ['atanh', 'arctanh', 'logaddexp', 'round', 'histc', 'addcdiv', 't', 'split', 'logical_or', 'true_divide', 'chunk', 'gcd', 'minimum', 'log2', 'cumsum', 'cosh', 'mul', 'all', 'asinh', 'arcsinh', 'square', 'put_', 'maximum', 'lerp', 'reshape', 'sum', 'triu', 'repeat', 'scatter_add', 'sinh', 'select', 'abs', 'absolute', '__abs__', 'mm', 'max', 'nan_to_num', '_to', 'atan2', 'arctan2', 'copy_', 'xlogy', 'unique', 'log10', 'sort', 'log1p', 'exp', 'masked_select', 'flatten', 'fmod', 'index_add', 'acos', 'arccos', 'sub_', '__isub__', 'argmax', 'bitwise_and', '__and__', 'sub', '__sub__', 'subtract', 'median', 'outer', 'kthvalue', 'isclose', 'mul_', '__imul__', 'var', 'asin', 'arcsin', 'exp_', 'expand_as', 'tile', 'floor', 'greater_equal', 'ge', 'take', 'narrow', 'rsqrt', 'scatter', 'addmv', 'addbmm', 'pow', '__pow__', 'not_equal', 'ne', 'std', 'isneginf', 'div_', '__itruediv__', 'sin', 'view_as', 'logical_not', 'argmin', 'neg', 'negative', 'div', 'divide', 'scatter_', 'dot', 'isinf', 'log', 'fill_', 'tril', 'logical_and', 'where', 'masked_fill_', 'bincount', 'acosh', 'arccosh', 'greater', 'gt', 'repeat_interleave', 'clone', 'mean', 'logsumexp', 'count_nonzero', 'topk', 'nansum', 'masked_fill', 'less', 'lt', 'addmm', 'transpose', 'new_ones', 'ceil', 'reciprocal', 'logical_xor', 'trunc', 'hardshrink', 'add_', '__iadd__', 'floor_divide', 'add', '__add__', 'tanh', 'logaddexp2', 'unsqueeze', 'erf', 'clamp', 'clip', 'remainder', 'allclose', 'matmul', 'sinc', 'less_equal', 'le', 'cos', 'gather', 'atan', 'arctan', 'type_as', 'inverse', 'fill_diagonal_', 'frac', 'bitwise_or', '__or__', 'diag', 'min', 'log_', 'unbind', 'roll', 'argsort', 'baddbmm', 'expm1', 'floor_divide_', '__ifloordiv__', 'bitwise_not', 'bitwise_xor', '__xor__', 'prod', 'sigmoid', 'index_select', 'new_zeros', 'eq', 'isfinite', 'any', 'erfc', 'sqrt', 'tan']
