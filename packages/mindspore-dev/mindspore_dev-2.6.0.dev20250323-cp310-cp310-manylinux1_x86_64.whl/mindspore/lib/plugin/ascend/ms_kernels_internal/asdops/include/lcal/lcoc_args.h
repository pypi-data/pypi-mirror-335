/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef LCCL_LCOC_ARGS_H
#define LCCL_LCOC_ARGS_H

constexpr int64_t WORKSPACE_REDUCE_SIZE = 4000000;
#include <map>
#include "hccl_types.h"

#pragma once
namespace Lcal {
const constexpr int32_t INT8_ELE_SIZE = 1;
const constexpr int32_t FP_BF_16_ELE_SIZE = 2;
constexpr uint32_t ALIGN_BYTES = 512;
enum CoCDataTypeDesc : int {
    COC_DATA_TYPE_UNDEFINED = -1,
    FP16FP16_FP32_FP16 = 0,   // 无量化，无反量化
    BF16BF16_FP32_BF16 = 1,   // 无量化，无反量化
    INT8INT8_INT32_FP16 = 2,  // W8A8，未融合量化，随路反量化
    INT8INT8_INT32_BF16 = 3,  // W8A8，未融合量化，aiv反量化
    FP16INT8_INT32_FP16 = 4,  // W8A8，融合量化，随路反量化
    BF16INT8_INT32_BF16 = 5,  // W8A8，融合量化，aiv反量化
    FP16INT8_FP32_FP16 = 6,   // W8A16，融合伪量化，无反量化
    BF16INT8_FP32_BF16 = 7,   // W8A16，融合伪量化，无反量化
    FP16INT4_FP32_FP16 = 8,   // W4A16，融合伪量化，无反量化
    BF16INT4_FP32_BF16 = 9,   // W4A16，融合伪量化，无反量化
    COC_DATA_TYPE_DESC_MAX = 10,
};

const std::map<CoCDataTypeDesc, int32_t> COC_TYPE2ELE_SIZE = {
    { FP16FP16_FP32_FP16, FP_BF_16_ELE_SIZE }, { BF16BF16_FP32_BF16, FP_BF_16_ELE_SIZE },
    { INT8INT8_INT32_FP16, INT8_ELE_SIZE },    { INT8INT8_INT32_BF16, INT8_ELE_SIZE },
    { FP16INT8_INT32_FP16, INT8_ELE_SIZE },    { BF16INT8_INT32_BF16, INT8_ELE_SIZE },
    { FP16INT8_FP32_FP16, FP_BF_16_ELE_SIZE }, { BF16INT8_FP32_BF16, FP_BF_16_ELE_SIZE },
    { FP16INT4_FP32_FP16, FP_BF_16_ELE_SIZE }, { BF16INT4_FP32_BF16, FP_BF_16_ELE_SIZE }
};

const std::map<CoCDataTypeDesc, HcclDataType> COC_TYPE2HCCL_TYPE = {
    { FP16FP16_FP32_FP16, HCCL_DATA_TYPE_FP16 },  { BF16BF16_FP32_BF16, HCCL_DATA_TYPE_BFP16 },
    { INT8INT8_INT32_FP16, HCCL_DATA_TYPE_FP16 }, { INT8INT8_INT32_BF16, HCCL_DATA_TYPE_BFP16 },
    { FP16INT8_INT32_FP16, HCCL_DATA_TYPE_FP16 }, { BF16INT8_INT32_BF16, HCCL_DATA_TYPE_BFP16 },
    { FP16INT8_FP32_FP16, HCCL_DATA_TYPE_FP16 },  { BF16INT8_FP32_BF16, HCCL_DATA_TYPE_BFP16 },
    { FP16INT4_FP32_FP16, HCCL_DATA_TYPE_FP16 },  { BF16INT4_FP32_BF16, HCCL_DATA_TYPE_BFP16 }
};

struct WorkspaceDetail {
    int64_t matrixActivationSize{ 0 };
    int64_t matrixWeightSize{ 0 };
    int64_t matrixIntermediateSize{ 0 };
    int64_t formatDequantParamSize{ 0 };

    int64_t GetSize() const
    {
        return matrixActivationSize + matrixWeightSize + matrixIntermediateSize +
               formatDequantParamSize + WORKSPACE_REDUCE_SIZE;
    }
};
}
#endif  // LCCL_LCOC_ARGS_H