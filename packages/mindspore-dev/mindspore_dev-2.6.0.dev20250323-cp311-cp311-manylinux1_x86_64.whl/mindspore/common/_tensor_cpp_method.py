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

tensor_cpp_methods = ['matmul', 'clone', '_to', 'mean', 'inverse', 'unbind', 'tile', 'cosh', 'reciprocal', 'split', 'mm', 'erfc', 'repeat_interleave', 'isfinite', 'log_', 'repeat', 'isneginf', 'reshape', 'put_', 'max', 'exp', 'log1p', 'log', 'eq', 'fill_', 'index_select', 'sin', 'view_as', 'atanh', 'arctanh', 'where', 'floor', 'mul_', '__imul__', 'min', 'nan_to_num', 'logaddexp', 'addcdiv', 'count_nonzero', 'lerp', 'logical_xor', 'atan', 'arctan', 'addmv', 'tanh', 'trunc', 'outer', 'bitwise_or', '__or__', 'greater_equal', 'ge', 'cos', 'greater', 'gt', 'copy_', 'round', 'tril', 'scatter', 'argmin', 'acos', 'arccos', 'tan', 'logical_or', 'nansum', 'expand_as', 'masked_fill', 'isinf', 'baddbmm', 'mul', 'narrow', 'cumsum', 'fill_diagonal_', 'masked_fill_', 'allclose', 'sub_', '__isub__', 'rsqrt', 'log10', 'sub', '__sub__', 'log2', 'logaddexp2', 'acosh', 'arccosh', 'add_', '__iadd__', 'asin', 'arcsin', 'bincount', 'expm1', 'unsqueeze', 'var', 'logical_not', 'all', 'histc', 'argsort', 'index_add', 'fmod', 'exp_', 'erf', 'topk', 'dot', 'sigmoid', 'median', 'add', '__add__', 'maximum', 'div_', '__itruediv__', 'less', 'lt', 'scatter_', 'sort', 'diag', 'chunk', 'subtract', 'sinh', 'select', 'atan2', 'arctan2', 'unique', 'triu', 'any', 'ceil', 'bitwise_xor', '__xor__', 'take', 'roll', 'floor_divide_', '__ifloordiv__', 'new_zeros', 'kthvalue', 'gather', 'bitwise_not', 'square', 'scatter_add', 'prod', 'new_ones', 'gcd', 'div', 'divide', 'isclose', 't', 'neg', 'negative', 'bitwise_and', '__and__', 'argmax', 'flatten', 'sum', 'frac', 'std', 'asinh', 'arcsinh', 'logical_and', 'hardshrink', 'addbmm', 'pow', '__pow__', 'abs', '__abs__', 'absolute', 'masked_select', 'sinc', 'type_as', 'true_divide', 'logsumexp', 'clamp', 'clip', 'not_equal', 'ne', 'less_equal', 'le', 'transpose', 'minimum', 'xlogy', 'sqrt', 'floor_divide', 'addmm', 'remainder']
