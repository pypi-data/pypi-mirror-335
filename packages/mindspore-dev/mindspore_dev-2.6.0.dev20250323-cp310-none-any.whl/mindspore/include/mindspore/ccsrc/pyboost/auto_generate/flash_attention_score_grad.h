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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FLASHATTENTIONSCOREGRAD_H_
#define MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FLASHATTENTIONSCOREGRAD_H_

#include "mindspore/ccsrc/pyboost/op_runner.h"
#include "mindspore/ccsrc/pyboost/op_register.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
class PYBOOST_API FlashAttentionScoreGrad : public pyboost::OpRunner {
 public:
  FlashAttentionScoreGrad(PrimitivePtr primitive, const DeviceContext *device_context)
      : OpRunner(std::move(primitive), device_context) {}
  ~FlashAttentionScoreGrad() override = default;

  virtual std::tuple<mindspore::tensor::BaseTensorPtr,mindspore::tensor::BaseTensorPtr,mindspore::tensor::BaseTensorPtr,mindspore::tensor::BaseTensorPtr> Call(const mindspore::tensor::BaseTensorPtr &query_tensor, const mindspore::tensor::BaseTensorPtr &key_tensor, const mindspore::tensor::BaseTensorPtr &value_tensor, const mindspore::tensor::BaseTensorPtr &dy_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &pse_shift_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &drop_mask_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &padding_mask_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &atten_mask_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &softmax_max_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &softmax_sum_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &softmax_in_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &attention_in_tensor, const std::optional<mindspore::ValueTuplePtr> &prefix, const std::optional<mindspore::ValueTuplePtr> &actual_seq_qlen, const std::optional<mindspore::ValueTuplePtr> &actual_seq_kvlen, const mindspore::Int64ImmPtr &head_num, const mindspore::FP32ImmPtr &keep_prob, const mindspore::FP32ImmPtr &scale_value, const mindspore::Int64ImmPtr &pre_tokens, const mindspore::Int64ImmPtr &next_tokens, const mindspore::Int64ImmPtr &inner_precise, const mindspore::Int64ImmPtr &input_layout, const mindspore::Int64ImmPtr &sparse_mode) = 0;
  bool output_is_tuple() const override { return true; }

 protected:
  static const std::string &op_name() {return op_name_;}

  inline static std::string op_name_ = "FlashAttentionScoreGrad";
};

}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FLASHATTENTIONSCOREGRAD_H_
