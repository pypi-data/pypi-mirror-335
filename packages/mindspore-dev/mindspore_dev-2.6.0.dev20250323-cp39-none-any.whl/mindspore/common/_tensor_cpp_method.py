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

tensor_cpp_methods = ['greater', 'gt', 'atan', 'arctan', 'nansum', 'log10', 'split', 'rsqrt', 'new_ones', 'remainder', 'sqrt', 'sigmoid', 'repeat', 'floor', 'masked_select', 'outer', 'clamp', 'clip', 'inverse', 'erf', 'count_nonzero', 'fill_', 'frac', 'mean', 'log_', 'masked_fill', 'div_', '__itruediv__', 'logsumexp', 'copy_', 'all', 'tile', 'mul', 'min', 'erfc', 'addcdiv', 'hardshrink', 'sin', 'exp_', 'addmv', 'scatter_', 'ceil', 'sinc', 'less_equal', 'le', 'nan_to_num', 'tanh', 'take', 'reciprocal', 'asin', 'arcsin', 'minimum', 'dot', 'mul_', '__imul__', 'new_zeros', 'logical_or', 'baddbmm', 'expm1', 'lerp', 'maximum', 'bitwise_xor', '__xor__', 'bitwise_not', 'where', 'isneginf', 'sort', 'eq', 'less', 'lt', 'narrow', 'xlogy', 'greater_equal', 'ge', 'sub_', '__isub__', 'kthvalue', 'type_as', 'any', 'add', '__add__', 'not_equal', 'ne', 'repeat_interleave', 'logical_not', 'isfinite', 'index_select', 'acosh', 'arccosh', 'mm', 't', 'allclose', 'index_add', 'unique', 'floor_divide_', '__ifloordiv__', 'bitwise_or', '__or__', 'div', 'divide', 'exp', 'isclose', 'diag', 'asinh', 'arcsinh', 'unsqueeze', 'log', 'cumsum', 'tan', 'select', 'log2', 'square', 'gcd', 'sum', 'logical_xor', 'reshape', 'acos', 'arccos', 'expand_as', 'add_', '__iadd__', 'argmin', 'bitwise_and', '__and__', 'put_', 'chunk', 'addbmm', 'atanh', 'arctanh', '_to', 'cosh', 'cos', 'roll', 'view_as', 'scatter', 'addmm', 'tril', 'logaddexp2', 'unbind', 'trunc', 'abs', 'absolute', '__abs__', 'neg', 'negative', 'gather', 'isinf', 'var', 'subtract', 'median', 'masked_fill_', 'max', 'argmax', 'scatter_add', 'atan2', 'arctan2', 'triu', 'flatten', 'topk', 'sub', '__sub__', 'fmod', 'floor_divide', 'sinh', 'round', 'argsort', 'fill_diagonal_', 'histc', 'log1p', 'clone', 'matmul', 'transpose', 'std', 'logical_and', 'prod', 'bincount', 'true_divide', 'logaddexp', 'pow', '__pow__']
