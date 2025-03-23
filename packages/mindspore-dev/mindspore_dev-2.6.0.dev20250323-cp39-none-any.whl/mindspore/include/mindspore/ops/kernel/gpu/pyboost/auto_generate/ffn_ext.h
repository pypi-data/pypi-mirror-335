/**
 * Copyright 2023 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_GPU_KERNEL_PYBOOST_FFNEXT_GPU_H_
#define MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_GPU_KERNEL_PYBOOST_FFNEXT_GPU_H_

#include "mindspore/ccsrc/pyboost/auto_generate/ffn_ext.h"
#include "ir/tensor.h"
#include "ir/scalar.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
class FFNExtGPU : public pyboost::FFNExt {
 public:
  FFNExtGPU(PrimitivePtr primitive, const DeviceContext *device_context)
    : FFNExt(std::move(primitive), device_context) {}
  ~FFNExtGPU() = default;

  mindspore::tensor::BaseTensorPtr Call(const mindspore::tensor::BaseTensorPtr &x_tensor, const mindspore::tensor::BaseTensorPtr &weight1_tensor, const mindspore::tensor::BaseTensorPtr &weight2_tensor, const std::optional<mindspore::ValueTuplePtr> &expertTokens, const std::optional<mindspore::tensor::BaseTensorPtr> &bias1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &bias2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &scale_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &offset_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &deqScale1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &deqScale2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_scale1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_scale2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_offset1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_offset2_tensor, const mindspore::Int64ImmPtr &activation, const mindspore::Int64ImmPtr &inner_precise) override;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_GPU_KERNEL_PYBOOST_FFNEXT_GPU_H_
