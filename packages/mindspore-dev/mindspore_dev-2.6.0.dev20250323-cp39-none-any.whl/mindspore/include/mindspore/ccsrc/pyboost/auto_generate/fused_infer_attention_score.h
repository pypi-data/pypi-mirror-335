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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FUSEDINFERATTENTIONSCORE_H_
#define MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FUSEDINFERATTENTIONSCORE_H_

#include "mindspore/ccsrc/pyboost/op_runner.h"
#include "mindspore/ccsrc/pyboost/op_register.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
class PYBOOST_API FusedInferAttentionScore : public pyboost::OpRunner {
 public:
  FusedInferAttentionScore(PrimitivePtr primitive, const DeviceContext *device_context)
      : OpRunner(std::move(primitive), device_context) {}
  ~FusedInferAttentionScore() override = default;

  virtual std::tuple<mindspore::tensor::BaseTensorPtr,mindspore::tensor::BaseTensorPtr> Call(const mindspore::tensor::BaseTensorPtr &query_tensor, const mindspore::ValueTuplePtr &key_tensor_list, const mindspore::ValueTuplePtr &value_tensor_list, const std::optional<mindspore::tensor::BaseTensorPtr> &pse_shift_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &attn_mask_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &actual_seq_lengths_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &actual_seq_lengths_kv_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &dequant_scale1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &quant_scale1_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &dequant_scale2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &quant_scale2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &quant_offset2_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_scale_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &antiquant_offset_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &block_table_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &query_padding_size_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &kv_padding_size_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &key_antiquant_scale_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &key_antiquant_offset_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &value_antiquant_scale_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &value_antiquant_offset_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &key_shared_prefix_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &value_shared_prefix_tensor, const std::optional<mindspore::tensor::BaseTensorPtr> &actual_shared_prefix_len_tensor, const mindspore::Int64ImmPtr &num_heads, const mindspore::FP32ImmPtr &scale_value, const mindspore::Int64ImmPtr &pre_tokens, const mindspore::Int64ImmPtr &next_tokens, const mindspore::Int64ImmPtr &input_layout, const mindspore::Int64ImmPtr &num_key_value_heads, const mindspore::Int64ImmPtr &sparse_mode, const mindspore::Int64ImmPtr &inner_precise, const mindspore::Int64ImmPtr &block_size, const mindspore::Int64ImmPtr &antiquant_mode, const mindspore::BoolImmPtr &softmax_lse_flag, const mindspore::Int64ImmPtr &key_antiquant_mode, const mindspore::Int64ImmPtr &value_antiquant_mode) = 0;
  bool output_is_tuple() const override { return true; }

 protected:
  static const std::string &op_name() {return op_name_;}

  inline static std::string op_name_ = "FusedInferAttentionScore";
};

}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_FUSEDINFERATTENTIONSCORE_H_
