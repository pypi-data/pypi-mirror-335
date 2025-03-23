/*
 * Copyright (c) 2024 Huawei Technologies Co., Ltd.
 * This file is a part of the CANN Open Software.
 * Licensed under CANN Open Software License Agreement Version 1.0 (the "License").
 * Please refer to the License for details. You may not use this file except in compliance with the License.
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE.
 * See LICENSE in the root of the software repository for the full text of the License.
 */
#ifndef LCAL_TILING_FUNC_H
#define LCAL_TILING_FUNC_H

#include <map>
#include <vector>
#include <cstdint>
#include "lcal_types.h"
#include "tiling_args.h"

#pragma once
namespace Lcal {
    struct TilingValue {
        int32_t value = -1;
        std::map<int, std::vector<std::vector<int>>> conditionMap = {};
    };

    int32_t CeilDev(int32_t num, int32_t div);
    int32_t RoundNum(int32_t num, int32_t rnd);
    void UpdateValue(int32_t &x, int32_t &y);
    double GetMTETime(double mknGB, int32_t m0, int32_t n0, double aBindWidth = 3.0, double bBindWidth = 3.0);
    int32_t GetValueFromMKNConditionMap(int32_t m, int32_t k, int32_t n,
                                        int32_t defaultValue,
                                        std::map<int, std::vector<std::vector<int>>> conditionMap);
    bool Is910B(const ChipName &chipName);
    bool Is91093(const ChipName &chipName);
    void SetTilingParam(PPTilingData &ppTilingData,
                        CommTilingData &commTilingData,
                        std::map<int*, TilingValue> TilingParamMap);
    void SetSecondCoreSplitTling(CommTilingData &commTilingData);
    void SetTilingParam2D(PPTilingData &ppTilingData,
                          CommTilingData &commTilingData,
                          std::map<int*, TilingValue> TilingParamMap);
}

#endif // LCAL_TILING_FUNC_H
